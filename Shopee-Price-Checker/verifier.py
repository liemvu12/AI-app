"""
verifier.py
Module xử lý thông minh:
1. Fuzzy matching tìm đúng phân loại (Model/Variant) mong muốn.
2. Kiểm tra tồn kho (Stock).
3. Quét từ khóa rủi ro trong bình luận 1-2 sao (hàng giả, lừa đảo, trâu cày, rỉ sét).
4. Tính toán mức giá thị trường (Median Benchmark) và lọc giá mồi/ngoại lai.
"""

import re
import statistics
from typing import List, Dict, Any, Optional

# Danh sách từ khóa rủi ro cốt lõi trong bình luận 1-2 sao (đã đơn giản hóa)
RED_FLAG_KEYWORDS = [
    "lừa đảo", "lua dao", "hàng giả", "hang gia", "fake", "nhái",
    "trâu cày", "trau cay", "rỉ sét", "cháy", "không lên", "chối bỏ"
]

# Từ khóa thường là sản phẩm mồi (phụ kiện kèm theo trong bài đăng máy chính)
BAIT_KEYWORDS = [
    "keo tản nhiệt", "keo tan nhiet", "dây nguồn", "day nguon", "cáp sata", "cap sata",
    "chặn main", "fe chặn", "vỏ hộp", "box rỗng", "chỉ đế", "chân đế", "cường lực", "ốp lưng",
    "fan tản nhiệt", "quạt tản nhiệt", "quạt case", "fan case", "fan led", "fan rgb",
    "chỉ quạt", "chỉ fan"
]


def is_bait_name(name_norm: str) -> bool:
    """Kiểm tra tên phân loại có phải là phụ kiện mồi giá rẻ hay không."""
    # Bỏ qua các cụm từ mô tả CPU bình thường như 'không fan', 'kèm fan'
    cleaned = name_norm
    for phrase in ["không fan", "khong fan", "ko fan", "k fan", "kèm fan", "kem fan", "không tản", "kèm tản"]:
        cleaned = cleaned.replace(phrase, "")
    return any(b in cleaned for b in BAIT_KEYWORDS)


def normalize_text(text: str) -> str:
    """Chuẩn hóa chuỗi văn bản: chuyển chữ thường, loại bỏ ký tự đặc biệt thừa."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def is_model_in_stock(m: Dict[str, Any]) -> bool:
    """Kiểm tra biến thể có thực sự còn hàng không (qua has_stock, is_grayout, hoặc stock > 0)."""
    if m.get("has_stock") is False or m.get("is_grayout") is True:
        return False
    if m.get("has_stock") is True:
        return True
    stock = m.get("stock", 0)
    if isinstance(stock, int):
        return stock > 0
    return True


def match_variant(
    models: List[Dict[str, Any]], 
    target_variant: Optional[str] = None,
    keyword: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    So khớp phân loại (model) từ danh sách biến thể của Shopee.
    - Kết hợp từ khóa chính (keyword) và phân loại mong muốn (target_variant).
    - Tìm model khớp nhất với sản phẩm cần mua (ví dụ đúng dòng CPU, đúng dung lượng RAM).
    - Giữ nguyên trạng thái tồn kho thật để phát hiện chính xác trường hợp hết hàng.
    """
    if not models:
        return None

    # Tập hợp các từ khóa tìm kiếm
    search_query = ""
    if keyword and target_variant:
        search_query = f"{keyword} {target_variant}"
    elif target_variant:
        search_query = target_variant
    elif keyword:
        search_query = keyword

    target_tokens = set(normalize_text(search_query).split())
    # Loại bỏ các từ quá chung chung khỏi target_tokens nếu có từ khóa cụ thể hơn
    generic_words = {"mua", "bán", "giá", "cũ", "mới", "new", "socket", "lga"}
    specific_tokens = target_tokens - generic_words if len(target_tokens) > 1 else target_tokens

    best_match = None
    best_score = -999

    for m in models:
        name_norm = normalize_text(m.get("name", ""))
        model_tokens = set(name_norm.split())

        # Tính điểm khớp
        score = 0
        overlap = len(specific_tokens.intersection(model_tokens))
        score += overlap * 3

        # Nếu cụm từ khóa nằm trọn trong tên phân loại
        if normalize_text(target_variant or "") and normalize_text(target_variant or "") in name_norm:
            score += 4
        if keyword and normalize_text(keyword) in name_norm:
            score += 6

        # Phạt nặng phụ kiện mồi
        if is_bait_name(name_norm):
            score -= 10

        # Ưu tiên nhẹ cho sản phẩm còn hàng nếu điểm khớp bằng nhau
        if is_model_in_stock(m):
            score += 0.5

        if score > best_score:
            best_score = score
            best_match = m

    # Nếu có model khớp điểm dương
    if best_score > 0 and best_match:
        return best_match

    # Fallback: Nếu không tìm thấy model khớp đặc thù, ưu tiên model còn hàng không phải mồi
    for m in models:
        name_norm = normalize_text(m.get("name", ""))
        if not is_bait_name(name_norm) and is_model_in_stock(m):
            return m

    return models[0]


def analyze_reviews(ratings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Phân tích đơn giản hóa bình luận 1-2 sao để quét nhanh rủi ro lừa đảo / hàng lỗi.
    """
    if not ratings:
        return {
            "risk_level": "SAFE",
            "red_flags_count": 0,
            "detected_issues": [],
            "risk_score": 0
        }

    detected_issues = []
    red_flag_hits = 0

    for r in ratings:
        star = r.get("rating_star", 5)
        if star in [1, 2]:
            comment = normalize_text(r.get("comment", ""))
            if comment:
                matched = [kw for kw in RED_FLAG_KEYWORDS if kw in comment]
                if matched:
                    red_flag_hits += len(matched)
                    detected_issues.append({
                        "star": star,
                        "matched_keywords": matched,
                        "snippet": comment[:80] + "..." if len(comment) > 80 else comment
                    })

    if red_flag_hits >= 2 or any("lừa đảo" in issue["snippet"] or "hàng giả" in issue["snippet"] for issue in detected_issues):
        risk_level = "HIGH_RISK"
    elif red_flag_hits == 1:
        risk_level = "WARNING"
    else:
        risk_level = "SAFE"

    return {
        "risk_level": risk_level,
        "red_flags_count": red_flag_hits,
        "detected_issues": detected_issues[:3],
        "risk_score": 100 if risk_level == "HIGH_RISK" else (50 if risk_level == "WARNING" else 0)
    }



def calculate_price_benchmark(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Đối chiếu giá giữa các shop (Cross-shop price benchmark):
    - Tính Median (giá trung vị)
    - Nhận diện các shop có giá bất thường (giá mồi quá thấp hoặc giá quá cao)
    """
    valid_prices = [it["matched_price"] for it in items if it.get("matched_price", 0) > 0]
    
    if not valid_prices:
        return {
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "recommended_range": (0, 0),
            "annotated_items": items
        }

    med = statistics.median(valid_prices)
    min_p = min(valid_prices)
    max_p = max(valid_prices)

    # Đánh dấu từng item
    for it in items:
        price = it.get("matched_price", 0)
        if price <= 0:
            it["price_status"] = "OUT_OF_STOCK"
            continue

        if price < 0.65 * med:
            it["price_status"] = "SUSPICIOUS_LOW"  # Nghi ngờ giá mồi phụ kiện hoặc hàng dởm
            it["price_warning"] = f"Giá thấp bất thường ({price:,}đ so với trung vị {int(med):,}đ)"
        elif price > 1.45 * med:
            it["price_status"] = "OVERPRICED"
            it["price_warning"] = f"Giá cao hơn nhiều so với thị trường ({price:,}đ)"
        else:
            it["price_status"] = "REASONABLE"
            it["price_warning"] = None

    return {
        "median_price": int(med),
        "min_price": min_p,
        "max_price": max_p,
        "recommended_range": (int(0.85 * med), int(1.15 * med)),
        "annotated_items": items
    }


def calculate_final_checkout_price(
    item_price: int,
    shipping_info: Optional[Dict[str, Any]] = None,
    shop_vouchers: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Xác định giá cuối cùng sau phí vận chuyển và voucher (Mô phỏng chọn mua trong giỏ hàng):
    - Base price (tiền hàng thật của phân loại)
    - Phí vận chuyển gốc và mức hỗ trợ / freeship thực tế theo địa chỉ người dùng
    - Voucher giảm giá tối ưu nhất của Shop (nếu đạt điều kiện đơn tối thiểu min_basket)
    - TUYỆT ĐỐI KHÔNG THANH TOÁN (Chỉ lấy tổng tiền thanh toán dự kiến để đối soát)
    """
    if item_price <= 0:
        return {
            "base_price": 0,
            "shipping_fee": 0,
            "shipping_original": 0,
            "shipping_discount": 0,
            "voucher_discount": 0,
            "applied_voucher_code": None,
            "final_price": 0,
            "buyer_location": "N/A",
            "safety_guarantee": "NO_PAYMENT_INTERACTION (CHỈ MÔ PHỎNG GIỎ HÀNG - TUYỆT ĐỐI KHÔNG THANH TOÁN)"
        }

    ship_orig = 0
    ship_fee = 0
    ship_discount = 0
    buyer_loc = "N/A"

    if shipping_info:
        ship_orig = shipping_info.get("shipping_original", 0)
        ship_fee = shipping_info.get("shipping_fee", 0)
        ship_discount = shipping_info.get("shipping_discount", 0)
        buyer_loc = shipping_info.get("buyer_location", "N/A")

    # Tìm voucher shop tốt nhất có thể áp dụng cho mức giá sản phẩm này
    best_voucher = None
    best_voucher_discount = 0

    if shop_vouchers:
        for v in shop_vouchers:
            min_basket = v.get("min_basket_vnd", 0)
            if item_price >= min_basket:
                disc = v.get("discount_vnd", 0)
                pct = v.get("discount_percentage", 0)
                if pct > 0:
                    disc_from_pct = int(item_price * pct / 100)
                    disc = max(disc, disc_from_pct)
                if disc > best_voucher_discount:
                    best_voucher_discount = disc
                    best_voucher = v.get("code")

    final_total = max(0, item_price + ship_fee - best_voucher_discount)

    return {
        "base_price": item_price,
        "shipping_original": ship_orig,
        "shipping_discount": ship_discount,
        "shipping_fee": ship_fee,
        "voucher_discount": best_voucher_discount,
        "applied_voucher_code": best_voucher,
        "final_price": final_total,
        "buyer_location": buyer_loc,
        "safety_guarantee": "NO_PAYMENT_INTERACTION (CHỈ MÔ PHỎNG GIỎ HÀNG - TUYỆT ĐỐI KHÔNG THANH TOÁN)"
    }

