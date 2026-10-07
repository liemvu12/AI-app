"""
test_verifier.py
Kiểm thử logic của module verifier:
1. So khớp đúng model/phân loại chính, bỏ qua giá mồi phụ kiện.
2. Kiểm tra tồn kho (stock).
3. Quét phát hiện review rủi ro (lừa đảo, trâu cày, rỉ sét).
4. Phân tích giá thị trường (Median Benchmark) và phát hiện giá mồi quá thấp hoặc giá quá cao.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from verifier import (
    match_variant, 
    analyze_reviews, 
    calculate_price_benchmark,
    calculate_final_checkout_price
)

def test_variant_matching_bait_price():
    # Giả lập sản phẩm CPU i5 10400F bị người bán treo phụ kiện "Keo tản nhiệt" 20k
    models = [
        {"model_id": 1, "name": "Keo tản nhiệt MX4 4g", "price": 2500000000, "stock": 50}, # 25k (giá Shopee x100,000)
        {"model_id": 2, "name": "Fan tản nhiệt CR1000", "price": 28000000000, "stock": 10}, # 280k
        {"model_id": 3, "name": "CPU i5 10400F Tray không fan", "price": 185000000000, "stock": 15}, # 1.85tr
        {"model_id": 4, "name": "CPU i5 10400F Box chính hãng", "price": 215000000000, "stock": 5}, # 2.15tr
    ]
    
    # Ca 1: Người dùng tìm phân loại "Tray"
    matched_tray = match_variant(models, target_variant="tray")
    assert matched_tray is not None
    assert matched_tray["model_id"] == 3
    assert "Tray" in matched_tray["name"]
    print("[PASS] Test khớp đúng phân loại 'tray', né giá mồi keo tản nhiệt 25k.")

    # Ca 2: Người dùng tìm phân loại "Box"
    matched_box = match_variant(models, target_variant="box")
    assert matched_box is not None
    assert matched_box["model_id"] == 4
    assert "Box" in matched_box["name"]
    print("[PASS] Test khớp đúng phân loại 'box'.")

    # Ca 3: Người dùng không nói rõ phân loại -> Tự né keo tản nhiệt/fan mồi
    matched_auto = match_variant(models, target_variant=None)
    assert matched_auto is not None
    assert matched_auto["model_id"] in [3, 4]
    print("[PASS] Test tự động né phụ kiện mồi khi không có target_variant.")


def test_review_analysis():
    # Đánh giá bình thường / tích cực
    good_reviews = [
        {"rating_star": 5, "comment": "Hàng đẹp đóng gói cẩn thận shop giao nhanh"},
        {"rating_star": 5, "comment": "Test chạy ngon lành cành đào"},
    ]
    res_good = analyze_reviews(good_reviews)
    assert res_good["risk_level"] == "SAFE"
    assert res_good["red_flags_count"] == 0
    print("[PASS] Test đánh giá shop uy tín (SAFE).")

    # Đánh giá có phốt trâu cày / rỉ sét
    bad_reviews = [
        {"rating_star": 1, "comment": "Shop lừa đảo, hàng trâu cày rỉ sét hết về cắm không lên"},
        {"rating_star": 2, "comment": "Hàng cũ nát chân cắm cháy xém, nhắn tin đòi bảo hành thì chối bỏ"},
    ]
    res_bad = analyze_reviews(bad_reviews)
    assert res_bad["risk_level"] in ["WARNING", "HIGH_RISK"]
    assert res_bad["red_flags_count"] >= 2
    assert len(res_bad["detected_issues"]) > 0
    print(f"[PASS] Test phát hiện shop rủi ro: {res_bad['risk_level']} với các lỗi: {res_bad['detected_issues']}")


def test_benchmark_calculation():
    items = [
        {"shop_name": "Shop A", "matched_price": 1850000},
        {"shop_name": "Shop B", "matched_price": 1900000},
        {"shop_name": "Shop C", "matched_price": 1820000},
        {"shop_name": "Shop D (Mồi)", "matched_price": 250000}, # Giá mồi quá rẻ
        {"shop_name": "Shop E (Ảo)", "matched_price": 3500000}, # Giá quá đắt
    ]
    benchmark = calculate_price_benchmark(items)
    assert benchmark["median_price"] == 1850000
    
    # Kiểm tra cờ cảnh báo
    shop_d = next(it for it in benchmark["annotated_items"] if it["shop_name"] == "Shop D (Mồi)")
    assert shop_d["price_status"] == "SUSPICIOUS_LOW"
    
    shop_e = next(it for it in benchmark["annotated_items"] if it["shop_name"] == "Shop E (Ảo)")
    assert shop_e["price_status"] == "OVERPRICED"
    
    print("[PASS] Test đối soát giá thị trường (Benchmark) và phát hiện giá ảo.")


def test_final_checkout_price():
    # 1. Sản phẩm có freeship: ship gốc 16.5k, giảm 16.5k => ship 0đ
    shipping_info = {
        "buyer_location": "Tây Hồ, Hà Nội",
        "shipping_original": 16500,
        "shipping_discount": 16500,
        "shipping_fee": 0
    }
    shop_vouchers = [
        {"code": "VOUCHER10K", "min_basket_vnd": 500000, "discount_vnd": 10000, "discount_percentage": 0},
        {"code": "VOUCHER50K", "min_basket_vnd": 2000000, "discount_vnd": 50000, "discount_percentage": 0}
    ]
    
    # Giá hàng 878.000đ: Đạt min_basket 500k => áp mã 10k, ship 0đ => final = 868.000đ
    calc = calculate_final_checkout_price(878000, shipping_info, shop_vouchers)
    assert calc["base_price"] == 878000
    assert calc["shipping_fee"] == 0
    assert calc["voucher_discount"] == 10000
    assert calc["applied_voucher_code"] == "VOUCHER10K"
    assert calc["final_price"] == 868000
    assert "TUYỆT ĐỐI KHÔNG THANH TOÁN" in calc["safety_guarantee"]
    print("[PASS] Test tính giá cuối cùng sau ship và voucher thành công!")


if __name__ == "__main__":
    print("--- BẮT ĐẦU CHẠY UNIT TEST VERIFIER ---")
    test_variant_matching_bait_price()
    test_review_analysis()
    test_benchmark_calculation()
    test_final_checkout_price()
    print("✅ TẤT CẢ CÁC TEST CASE ĐÃ VƯỢT QUA!")

