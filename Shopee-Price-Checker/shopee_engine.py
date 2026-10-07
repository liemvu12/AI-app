"""
shopee_engine.py
Module thu thập dữ liệu Shopee:
1. Nạp session từ session_state.json với quyền hạn đăng nhập thật.
2. Bóc tách chi tiết biến thể và bảng giá thật (VND) từng SKU bằng Playwright Edge headless qua endpoint PDP (`pdp/get_pc`).
3. Tự động kiểm tra trạng thái tồn kho thực tế (has_stock, is_grayout).
4. Khám phá các URL sản phẩm theo từ khóa qua Search Engine hoặc nhận danh sách URL trực tiếp.
"""

import sys
import os
import json
import time
import urllib.parse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_FILE = Path(__file__).parent / "session_state.json"


class ShopeeEngine:
    def __init__(self, session_path: Path = SESSION_FILE):
        self.session_path = session_path

    def get_item_details_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Bóc tách chi tiết biến thể, giá VND thật và trạng thái kho của danh sách link Shopee.
        Sử dụng trình duyệt Edge headless nạp phiên đăng nhập thật để lấy dữ liệu pdp/get_pc.
        """
        if not urls:
            return []

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as err:
            print(f"[!] Lỗi import Playwright: {err}")
            return []

        results = []

        with sync_playwright() as p:
            # Ưu tiên kênh Edge của máy người dùng
            browser = None
            for ch in ("msedge", "chrome", None):
                try:
                    browser = p.chromium.launch(
                        channel=ch,
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                    )
                    break
                except Exception:
                    continue

            if not browser:
                print("[!] Không thể khởi động trình duyệt.")
                return []

            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
            if self.session_path.exists():
                context_kwargs["storage_state"] = str(self.session_path)

            context = browser.new_context(**context_kwargs)

            for url in urls:
                page = context.new_page()
                pdp_data = {}

                def on_resp(resp):
                    if "pdp/get_pc" in resp.url and resp.status == 200:
                        try:
                            pdp_data.update(resp.json())
                        except Exception:
                            pass

                page.on("response", on_resp)

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    # Chờ tối đa 8 giây để bắt gói tin pdp/get_pc
                    for _ in range(16):
                        if pdp_data:
                            break
                        page.wait_for_timeout(500)
                except Exception as e:
                    if not pdp_data:
                        print(f"[!] Lỗi khi truy cập {url}: {e}")

                if pdp_data:
                    data = pdp_data.get("data", {})
                    item = data.get("item", {})
                    shop = data.get("shop_detailed", {})
                    prod_review = data.get("product_review", {})

                    # Xác định badge gian hàng
                    is_mall = shop.get("is_official_shop", False)
                    is_preferred = (
                        shop.get("is_preferred_plus_seller", False)
                        or shop.get("is_shopee_verified", False)
                        or shop.get("shopee_verified", False)
                    )
                    badge = "MALL" if is_mall else ("YÊU THÍCH" if is_preferred else "THƯỜNG")

                    # Lượt bán
                    sold_display = (
                        prod_review.get("sold_count_display")
                        or item.get("historical_sold")
                        or 0
                    )
                    try:
                        sold_num = int(str(sold_display).replace("k", "000").replace(".", "").replace("+", ""))
                    except Exception:
                        sold_num = 0

                    # Điểm đánh giá
                    rating_star = round(float(prod_review.get("rating_star") or item.get("item_rating", {}).get("rating_star") or 0.0), 1)

                    # Bóc tách models / phân loại
                    raw_models = item.get("models", [])
                    parsed_models = []
                    for m in raw_models:
                        # Giá Shopee được nhân với 100,000 (ví dụ 1.599.000đ là 159900000000)
                        raw_price = m.get("price") or 0
                        price_vnd = int(raw_price / 100000) if raw_price > 0 else 0

                        # Trạng thái kho thực tế
                        has_stock = m.get("has_stock", True)
                        is_grayout = m.get("is_grayout", False)
                        is_clickable = m.get("is_clickable", True)
                        actual_in_stock = (has_stock is not False) and (not is_grayout) and is_clickable

                        parsed_models.append({
                            "model_id": m.get("model_id") or m.get("modelid", 0),
                            "name": m.get("name", "Mặc định"),
                            "price": price_vnd,
                            "stock": 10 if actual_in_stock else 0,
                            "has_stock": actual_in_stock,
                            "is_grayout": is_grayout
                        })

                    # Nếu không có phân loại con (sản phẩm đơn)
                    if not parsed_models and (item.get("price") or item.get("price_min")):
                        single_price = int((item.get("price") or item.get("price_min", 0)) / 100000)
                        parsed_models.append({
                            "model_id": 0,
                            "name": "Bản tiêu chuẩn",
                            "price": single_price,
                            "stock": 10,
                            "has_stock": True,
                            "is_grayout": False
                        })

                    # Bóc tách thông tin vận chuyển và voucher của shop
                    prod_ship = data.get("product_shipping") or {}
                    addr = prod_ship.get("delivery_address") or {}
                    buyer_loc = f"{addr.get('city', '')}, {addr.get('state', '')}".strip(", ")
                    pre_channel = prod_ship.get("pre_selected_shipping_channel") or {}
                    p_orig = pre_channel.get("price_before_discount") or {}
                    p_actual = pre_channel.get("price") or {}
                    raw_ship_orig = p_orig.get("single_value", 0) if isinstance(p_orig, dict) else 0
                    raw_ship_actual = p_actual.get("single_value", 0) if isinstance(p_actual, dict) else 0

                    ship_orig_vnd = int(raw_ship_orig / 100000) if raw_ship_orig and raw_ship_orig > 0 else 0
                    ship_actual_vnd = int(raw_ship_actual / 100000) if raw_ship_actual and raw_ship_actual >= 0 else 0
                    ship_discount_vnd = max(0, ship_orig_vnd - ship_actual_vnd)

                    parsed_vouchers = []
                    for v in (data.get("shop_vouchers") or []):
                        raw_disc = v.get("discount_value", 0)
                        raw_min = v.get("min_basket_price", 0)
                        parsed_vouchers.append({
                            "code": v.get("voucher_code"),
                            "discount_vnd": int(raw_disc / 100000) if raw_disc > 0 else 0,
                            "min_basket_vnd": int(raw_min / 100000) if raw_min > 0 else 0,
                            "discount_percentage": v.get("discount_percentage", 0)
                        })

                    shipping_info = {
                        "buyer_location": buyer_loc or "Địa chỉ mặc định của bạn",
                        "shipping_channel": pre_channel.get("name", "Vận chuyển tiêu chuẩn"),
                        "shipping_original": ship_orig_vnd,
                        "shipping_discount": ship_discount_vnd,
                        "shipping_fee": ship_actual_vnd
                    }

                    item_id = item.get("item_id") or item.get("itemid")
                    shop_id = item.get("shop_id") or item.get("shopid") or shop.get("shopid")

                    results.append({
                        "item_id": item_id,
                        "shop_id": shop_id,
                        "name": item.get("title") or item.get("name", "Sản phẩm Shopee"),
                        "shop_name": shop.get("name", "Shop Shopee"),
                        "shop_badge": badge,
                        "rating_star": rating_star,
                        "sold": sold_num,
                        "models": parsed_models,
                        "shipping_info": shipping_info,
                        "shop_vouchers": parsed_vouchers,
                        "negative_reviews": [],
                        "url": url
                    })

                page.close()

            browser.close()

        return results

    def discover_product_urls(self, keyword: str, limit: int = 10) -> List[str]:
        """
        Tìm kiếm danh sách URL sản phẩm Shopee liên quan tới từ khóa qua Search Engine.
        """
        try:
            from curl_cffi import requests as c_requests
            query = f'site:shopee.vn "{keyword}" -list'
            ddg_url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
            r = c_requests.get(ddg_url, impersonate="chrome124", timeout=8)
            links = re.findall(r'uddg=([^&"\']+)', r.text)
            decoded = [urllib.parse.unquote(l) for l in links if 'shopee.vn' in urllib.parse.unquote(l)]
            
            # Lọc URL sản phẩm dạng -i.{shop_id}.{item_id} hoặc /product/
            product_urls = []
            for u in decoded:
                clean = u.split("?")[0]
                if ("-i." in clean or "/product/" in clean) and "/list/" not in clean and "/search" not in clean:
                    if clean not in product_urls:
                        product_urls.append(clean)
                if len(product_urls) >= limit:
                    break
            if product_urls:
                return product_urls
        except Exception:
            pass

        return []

    def search_items(self, keyword: str, limit: int = 10, urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm và bóc tách danh sách sản phẩm.
        - Nếu có truyền sẵn danh sách `urls`, bóc tách trực tiếp.
        - Nếu không có `urls`, tự động khám phá link qua discover_product_urls.
        """
        target_urls = urls or []
        if not target_urls:
            target_urls = self.discover_product_urls(keyword, limit=limit)

        if not target_urls:
            print(f"[*] Không tìm thấy URL tự động cho '{keyword}'. Vui lòng cung cấp danh sách URLs cụ thể.")
            return []

        return self.get_item_details_batch(target_urls[:limit])

    def get_item_models(self, item_id: int, shop_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách phân loại (hỗ trợ tương thích ngược)."""
        url = f"https://shopee.vn/product/{shop_id}/{item_id}"
        items = self.get_item_details_batch([url])
        if items:
            return items[0].get("models", [])
        return []

    def get_item_negative_reviews(self, item_id: int, shop_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy đánh giá tiêu cực (hỗ trợ tương thích ngược)."""
        return []
