"""
check_price.py
Giao diện dòng lệnh (CLI Tool) và điều phối toàn bộ quy trình:
1. Nhận từ khóa tìm kiếm, phân loại mong muốn hoặc danh sách URLs cụ thể.
2. Nạp session từ session_state.json và lấy dữ liệu chi tiết biến thể qua ShopeeEngine.
3. Lọc shop uy tín (Mall, Yêu thích hoặc đánh giá cao, nhiều lượt bán).
4. Bóc tách cây phân loại, tìm chính xác phân loại cần mua và kiểm tra tồn kho thật.
5. Quét review tiêu cực 1-2 sao để phát hiện hàng lỗi/trâu cày.
6. Đối soát giá liên shop (Median Benchmark) để loại bỏ giá mồi rẻ bất thường.
7. Xuất kết quả dạng Bảng trực quan hoặc JSON sạch cho AI phân tích.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from shopee_engine import ShopeeEngine
from verifier import (
    match_variant, 
    analyze_reviews, 
    calculate_price_benchmark, 
    is_model_in_stock,
    calculate_final_checkout_price
)
from auth import is_session_valid


def format_currency(amount: int) -> str:
    """Format số tiền thành dạng 1.500.000đ"""
    return f"{amount:,}đ".replace(",", ".")


def run_check_price(
    keyword: str,
    target_variant: str = None,
    min_rating: float = 4.6,
    min_sold: int = 100,  # Quy tắc bắt buộc: số lượng lượt mua phải lớn hơn 100
    limit: int = 15,
    strict_shop: bool = False,
    output_format: str = "table",
    urls: Optional[List[str]] = None
) -> Dict[str, Any]:
    
    engine = ShopeeEngine()
    session_ok = is_session_valid()
    
    # 1. Tìm kiếm và bóc tách danh sách sản phẩm
    raw_results = engine.search_items(keyword=keyword, limit=limit, urls=urls)
    if not raw_results:
        return {
            "status": "error",
            "message": f"Không tìm thấy sản phẩm nào với từ khóa '{keyword}' hoặc kết nối bị gián đoạn.",
            "data": []
        }

    valid_candidates = []
    
    # 2. Lọc shop cơ bản & bóc tách từng sản phẩm
    for item in raw_results:
        # Lọc theo badge nếu bật strict_shop
        if strict_shop and item["shop_badge"] == "THƯỜNG":
            continue
            
        # Lọc theo đánh giá và lượt mua (Quy tắc bắt buộc: sold > 100)
        if item["rating_star"] > 0 and item["rating_star"] < min_rating:
            continue
        if item.get("sold", 0) <= min_sold:
            continue
            
        # Lấy cây biến thể (models) đã bóc tách từ PDP
        models = item.get("models", [])
        if not models:
            continue
            
        # Khớp đúng phân loại cần mua
        matched_model = match_variant(models, target_variant=target_variant, keyword=keyword)
        if not matched_model:
            continue
            
        matched_price = matched_model.get("price", 0)
        stock_status = is_model_in_stock(matched_model)
        
        # Bỏ qua nếu giá không hợp lệ
        if matched_price <= 0:
            continue
            
        # Phân tích review nếu có
        neg_reviews = item.get("negative_reviews", [])
        review_analysis = analyze_reviews(neg_reviews)

        # Mô phỏng chọn mua trong giỏ hàng để xác định giá cuối cùng sau ship và voucher
        # TUYỆT ĐỐI KHÔNG THANH TOÁN (NO_PAYMENT_GUARANTEE)
        checkout_details = calculate_final_checkout_price(
            item_price=matched_price,
            shipping_info=item.get("shipping_info"),
            shop_vouchers=item.get("shop_vouchers")
        )
        
        valid_candidates.append({
            "item_id": item["item_id"],
            "shop_id": item["shop_id"],
            "product_title": item["name"],
            "shop_name": item.get("shop_name", "Shop Shopee"),
            "shop_badge": item["shop_badge"],
            "rating_star": item["rating_star"],
            "sold": item["sold"],
            "matched_variant_name": matched_model.get("name", "Mặc định"),
            "matched_price": matched_price,
            "final_price": checkout_details["final_price"],
            "shipping_fee": checkout_details["shipping_fee"],
            "shipping_discount": checkout_details["shipping_discount"],
            "voucher_discount": checkout_details["voucher_discount"],
            "buyer_location": checkout_details["buyer_location"],
            "checkout_details": checkout_details,
            "stock": 10 if stock_status else 0,
            "has_stock": stock_status,
            "risk_level": review_analysis["risk_level"],
            "risk_score": review_analysis["risk_score"],
            "detected_issues": review_analysis["detected_issues"],
            "url": item["url"]
        })

    if not valid_candidates:
        return {
            "status": "not_found",
            "message": f"Không tìm thấy phân loại '{target_variant}' còn hàng ở các shop đạt tiêu chuẩn.",
            "data": []
        }

    # 3. Đối soát giá liên shop (Benchmark)
    benchmark = calculate_price_benchmark(valid_candidates)
    annotated_items = benchmark["annotated_items"]
    
    # 4. Sắp xếp: Ưu tiên SAFE/WARNING, giá từ thấp đến cao, còn hàng thật
    trusted_deals = [
        it for it in annotated_items 
        if it["risk_level"] != "HIGH_RISK" and it.get("price_status") == "REASONABLE" and it["has_stock"]
    ]
    trusted_deals.sort(key=lambda x: x["matched_price"])
    
    # Các lựa chọn khác (hết hàng, nghi ngờ giá mồi, hoặc rủi ro)
    other_deals = [it for it in annotated_items if it not in trusted_deals]

    result_payload = {
        "status": "success",
        "session_active": session_ok,
        "query": {
            "keyword": keyword,
            "target_variant": target_variant or "Mặc định",
            "strict_shop": strict_shop
        },
        "market_benchmark": {
            "median_price": benchmark["median_price"],
            "median_formatted": format_currency(benchmark["median_price"]),
            "min_price": benchmark["min_price"],
            "max_price": benchmark["max_price"],
            "recommended_range": f"{format_currency(benchmark['recommended_range'][0])} - {format_currency(benchmark['recommended_range'][1])}",
            "total_shops_checked": len(raw_results),
            "valid_options_found": len(valid_candidates),
            "trusted_options_count": len(trusted_deals)
        },
        "trusted_deals": trusted_deals,
        "other_deals_flagged": other_deals
    }

    return result_payload


def print_cli_table(result: Dict[str, Any]):
    if result.get("status") != "success":
        print(f"\n[!] {result.get('message', 'Không có kết quả.')}")
        return

    q = result["query"]
    bm = result["market_benchmark"]
    trusted = result["trusted_deals"]

    buyer_loc = trusted[0].get("buyer_location", "Địa chỉ mặc định") if trusted else "N/A"
    print("\n" + "=" * 115)
    print(f"🔍 KẾT QUẢ KIỂM ĐỊNH GIÁ SHOPEE: '{q['keyword']}' (Phân loại: '{q['target_variant']}')")
    print(f"📊 GIÁ TRUNG VỊ THỊ TRƯỜNG: {bm['median_formatted']} | KHOẢNG GIÁ HỢP LÝ: {bm['recommended_range']}")
    print(f"🏢 Tổng số shop kiểm tra: {bm['total_shops_checked']} | Lựa chọn đạt chuẩn: {bm['trusted_options_count']}")
    print(f"📍 Địa chỉ nhận hàng dự kiến: {buyer_loc}")
    print("🛡️ BẢO VỆ AN TOÀN: ĐỐI SOÁT GIỎ HÀNG XÁC ĐỊNH GIÁ & SHIP — TUYỆT ĐỐI KHÔNG THANH TOÁN (NO_PAYMENT_GUARANTEE)")
    print("=" * 115)

    if trusted:
        print("\n✅ CÁC LỰA CHỌN TỐT NHẤT (ĐÃ MÔ PHỎNG GIỎ HÀNG: CỘNG PHÍ SHIP THỰC TẾ & TRỪ VOUCHER SHOP):\n")
        print(f"{'STT':<4} | {'Phân loại chính xác':<22} | {'Tiền hàng':<12} | {'Ship (Giảm)':<15} | {'Voucher':<10} | {'GIÁ CUỐI CÙNG':<14} | {'Shop & Đánh giá':<18} | {'Link sản phẩm'}")
        print("-" * 140)
        for idx, item in enumerate(trusted[:8], 1):
            var_name = (item["matched_variant_name"] or "Bản tiêu chuẩn")[:20]
            price_str = format_currency(item["matched_price"])
            final_str = format_currency(item.get("final_price", item["matched_price"]))
            
            ship_fee = item.get("shipping_fee", 0)
            ship_disc = item.get("shipping_discount", 0)
            if ship_fee == 0 and ship_disc > 0:
                ship_str = "0đ (Freeship)"
            elif ship_fee == 0:
                ship_str = "0đ"
            else:
                ship_str = f"{ship_fee:,}đ"

            v_disc = item.get("voucher_discount", 0)
            voucher_str = f"-{v_disc:,}đ" if v_disc > 0 else "0đ"

            badge = item["shop_badge"]
            rating_str = f"{item['rating_star']}⭐ ({item['sold']})"
            shop_info = f"{item['shop_name'][:10]} ({rating_str})"[:18]
            
            print(f"{idx:<4} | {var_name:<22} | {price_str:<12} | {ship_str:<15} | {voucher_str:<10} | {final_str:<14} | {shop_info:<18} | {item['url']}")
    else:
        print("\n⚠️ Không tìm thấy deal nào còn hàng hoàn toàn sạch không rủi ro.")

    flagged = result.get("other_deals_flagged", [])
    if flagged:
        print("\n⚠️ CÁC GIAN HÀNG CÓ CẢNH BÁO RỦI RO / GIÁ ẢO / HẾT HÀNG (ĐÃ BỊ LỌC RA):\n")
        for item in flagged[:6]:
            warning_reasons = []
            if not item.get("has_stock"):
                warning_reasons.append("Hết hàng (Stock = 0)")
            if item["risk_level"] == "HIGH_RISK":
                warning_reasons.append("Phát hiện phốt trong review 1-2 sao")
            if item.get("price_status") == "SUSPICIOUS_LOW":
                warning_reasons.append("Giá thấp bất thường (nghi ngờ giá mồi)")
            if item.get("price_status") == "OVERPRICED":
                warning_reasons.append("Giá cao hơn nhiều so với thị trường")
            
            reasons_str = "; ".join(warning_reasons) if warning_reasons else "Cảnh báo chất lượng"
            print(f" - [{item['shop_badge']}] {item['product_title'][:40]}... ({item['matched_variant_name']}): {format_currency(item['matched_price'])} -> ❌ Lý do loại: {reasons_str}")
    
    print("\n" + "=" * 90 + "\n")


def run_interactive_wizard():
    """
    Quy trình tương tác chuẩn hóa:
    - Tra cứu đơn lẻ: Hỏi rõ mức giá/ngân sách mong muốn trước khi tìm.
    - Build hệ thống: Hỏi người dùng đã có sẵn những gì, lên danh sách cần mua và yêu cầu xác nhận trước khi tra giá.
    """
    print("\n" + "=" * 75)
    print("🎯 TRÌNH KHẢO SÁT & TRA CỨU GIÁ SHOPEE (SHOPEE PRICE CHECKER WIZARD)")
    print("=" * 75)
    print("Chọn nhu cầu của bạn:")
    print(" [1] Tra cứu thiết bị / linh kiện đơn lẻ")
    print(" [2] Lên danh sách build hệ thống (Case PC, Dàn Samsung DeX, Mini PC...)")
    choice = input("\n👉 Nhập lựa chọn (1 hoặc 2) [mặc định: 1]: ").strip() or "1"

    if choice == "2":
        print("\n" + "-" * 75)
        print("📌 [BƯỚC 1: KHẢO SÁT HỆ THỐNG CẦN BUILD & LINH KIỆN SẴN CÓ]")
        print("-" * 75)
        system_name = input("👉 Bạn muốn build hệ thống gì? (VD: Case PC Gaming, Dàn Samsung DeX...): ").strip() or "Hệ thống máy tính"
        budget_str = input("👉 Mức ngân sách dự kiến của bạn là bao nhiêu? (VD: 15tr, 2tr5, 5tr...): ").strip()
        already_have = input("👉 Hiện tại bạn ĐÃ CÓ SẴN những linh kiện/thiết bị gì rồi? (VD: màn hình, nguồn, chuột... hoặc Enter nếu chưa có): ").strip()

        print("\n" + "-" * 75)
        print("📌 [BƯỚC 2: LÊN DANH SÁCH CÁC MÓN CẦN MUA DỰ KIẾN]")
        print("-" * 75)
        print(f"Hệ thống: {system_name}")
        print(f"Ngân sách: {budget_str or 'Linh hoạt'}")
        print(f"Linh kiện đã có sẵn (không cần mua): {already_have or 'Chưa có'}")
        
        items_input = input("\n👉 Nhập danh sách các món cần mua (phân cách bằng dấu phẩy, VD: CPU i5 10400F, Main B460, RAM 16GB...): ").strip()
        if not items_input:
            print("⚠️ Bạn chưa nhập danh sách món cần mua. Thoát.")
            return

        items_list = [x.strip() for x in items_input.split(",") if x.strip()]
        print("\n📋 DANH SÁCH CÁC MÓN CẦN MUA ĐÃ ĐƯỢC THIẾT LẬP:")
        for idx, item in enumerate(items_list, 1):
            print(f"   [{idx}] {item}")

        print("\n" + "-" * 75)
        print("📌 [BƯỚC 3: YÊU CẦU XÁC NHẬN TRƯỚC KHI LÊN ĐƠN GIÁ]")
        print("-" * 75)
        confirm = input("❓ Bạn có xác nhận danh sách các món cần mua trên để tiến hành đối soát giá Shopee không? (y/n) [y]: ").strip().lower()
        if confirm not in ["", "y", "yes"]:
            print("❌ Đã hủy tra cứu theo yêu cầu của bạn. Vui lòng chạy lại khi cần điều chỉnh danh sách.")
            return

        print("\n✅ ĐÃ XÁC NHẬN! Đang bắt đầu tra cứu và đối soát giá từng linh kiện trên Shopee...\n")
        for item in items_list:
            print(f"\n🔍 >>> ĐANG TRA CỨU: {item} <<<")
            res = run_check_price(keyword=item, limit=5, output_format="table")
            print_cli_table(res)

    else:
        print("\n" + "-" * 75)
        print("📌 [KHẢO SÁT MỨC GIÁ THIẾT BỊ ĐƠN LẺ]")
        print("-" * 75)
        keyword = input("👉 Nhập tên thiết bị / sản phẩm cần tìm: ").strip()
        if not keyword:
            print("⚠️ Từ khóa không được để trống. Thoát.")
            return

        budget_req = input("👉 Bạn cần thiết bị trong khoảng mức giá bao nhiêu? (VD: dưới 1tr, 2-3tr, rẻ nhất...): ").strip()
        variant = input("👉 Phân loại mong muốn (VD: tray, box, 16gb, để trống nếu mặc định): ").strip() or None

        print(f"\n✅ Đã ghi nhận: Tìm '{keyword}' (Phân loại: {variant or 'Tự động'}), mức giá mong muốn: {budget_req or 'Không giới hạn'}")
        print("\n🔍 Đang tra cứu giá thực tế, kiểm tra tồn kho và quét phốt trên Shopee...\n")
        res = run_check_price(keyword=keyword, target_variant=variant, limit=10, output_format="table")
        print_cli_table(res)


def main():
    parser = argparse.ArgumentParser(description="Shopee Price Checker - Tra cứu giá thật & lọc shop uy tín")
    parser.add_argument("--keyword", "-k", type=str, default=None, help="Từ khóa sản phẩm cần tìm (VD: 'i5 10400f')")
    parser.add_argument("--variant", "-v", type=str, default=None, help="Phân loại mong muốn (VD: 'tray', 'box', '256gb')")
    parser.add_argument("--min-rating", type=float, default=4.6, help="Đánh giá sao tối thiểu của shop (mặc định: 4.6)")
    parser.add_argument("--min-sold", type=int, default=100, help="Lượt bán tối thiểu (mặc định: 100, bắt buộc > 100)")
    parser.add_argument("--limit", type=int, default=15, help="Số lượng shop kiểm tra (mặc định: 15)")
    parser.add_argument("--strict-shop", action="store_true", help="Chỉ chấp nhận Shopee Mall hoặc Shop Yêu Thích")
    parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="Định dạng kết quả xuất ra")
    parser.add_argument("--urls", "-u", nargs="*", default=None, help="Danh sách URL sản phẩm cụ thể cần đối soát")
    parser.add_argument("--interactive", "-i", action="store_true", help="Kích hoạt trình tương tác hỏi ngân sách, khảo sát đồ đã có và xác nhận danh sách cần mua")

    args = parser.parse_args()

    # Nếu người dùng chọn -i/--interactive hoặc chạy không kèm tham số keyword
    if args.interactive or (not args.keyword and not args.urls):
        run_interactive_wizard()
        return

    res = run_check_price(
        keyword=args.keyword,
        target_variant=args.variant,
        min_rating=args.min_rating,
        min_sold=args.min_sold,
        limit=args.limit,
        strict_shop=args.strict_shop,
        output_format=args.format,
        urls=args.urls
    )

    if args.format == "json":
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print_cli_table(res)


if __name__ == "__main__":
    main()

