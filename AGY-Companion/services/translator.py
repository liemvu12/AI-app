"""
Dịch vụ Dịch thuật và Nhận diện Ngôn ngữ (Fast Translation & Language Detection)
Sử dụng Google Translate Client endpoint tốc độ cao (<300ms) kèm MyMemory fallback và cache.
"""
import re
import urllib.request
import urllib.parse
import json
from typing import Tuple
from deep_translator import MyMemoryTranslator

# Cache trong bộ nhớ
_TRANSLATION_CACHE: dict[Tuple[str, str, str], str] = {}

# Regex phát hiện dấu tiếng Việt
VIETNAMESE_DIACRITICS_REGEX = re.compile(
    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]",
    re.IGNORECASE
)

# Từ không dấu phổ biến và đặc trưng trong tiếng Việt
COMMON_VI_UNACCENTED = {
    "toi", "minh", "giup", "tao", "ung", "dung", "bang", "lam", "sao", "khong",
    "duoc", "neu", "khi", "trong", "nay", "va", "voi", "cua", "cac", "nhung",
    "chay", "sua", "loi", "viet", "ham", "cau", "hinh", "thu", "muc", "chuc",
    "nang", "du", "an", "ma", "nguon", "bien", "tap", "tin"
}

# Các từ tiếng Anh phổ biến để phân biệt với tiếng Việt không dấu
COMMON_EN_WORDS = {
    "the", "is", "are", "was", "were", "and", "or", "of", "to", "in", "on", "at",
    "for", "with", "this", "that", "it", "from", "by", "as", "an", "a", "be",
    "have", "has", "had", "do", "does", "did", "can", "will", "would", "should",
    "could", "not", "no", "if", "then", "else", "function", "return", "error"
}


def detect_language(text: str) -> str:
    """
    Nhận diện văn bản là tiếng Việt ('vi') hay tiếng Anh ('en').
    """
    cleaned = text.strip().lower()
    if not cleaned:
        return "vi"
    
    # Bỏ qua các slash command
    if cleaned.startswith("/"):
        return "command"

    # Có dấu tiếng Việt chắc chắn 100% là tiếng Việt
    if VIETNAMESE_DIACRITICS_REGEX.search(cleaned):
        return "vi"
    
    # Phân tích từ không dấu so với từ tiếng Anh phổ biến
    words = re.findall(r"\b\w+\b", cleaned)
    if words:
        vi_word_count = sum(1 for w in words if w in COMMON_VI_UNACCENTED)
        en_word_count = sum(1 for w in words if w in COMMON_EN_WORDS)
        
        # Nếu có từ tiếng Anh phổ biến và số từ tiếng Anh áp đảo, xác định là tiếng Anh
        if en_word_count > vi_word_count:
            return "en"
        # Nếu không có từ tiếng Anh và có từ tiếng Việt đặc trưng không dấu
        if en_word_count == 0 and vi_word_count >= 1:
            return "vi"
        if vi_word_count >= 2 and (vi_word_count / len(words)) >= 0.25:
            return "vi"
            
    return "en"


def _google_translate_fast(text: str, sl: str, tl: str) -> str:
    """
    Gọi trực tiếp Google Translate client endpoint tốc độ cao (~200ms) qua HTTP POST.
    Hỗ trợ xử lý trọn vẹn văn bản dài, đa câu mà không bị giới hạn URL hay timeout.
    """
    url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={sl}&tl={tl}"
    data = urllib.parse.urlencode({"q": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
    )
    with urllib.request.urlopen(req, timeout=6.0) as resp:
        raw_data = resp.read().decode("utf-8")
        parsed = json.loads(raw_data)
        if isinstance(parsed, list):
            items = []
            for item in parsed:
                if isinstance(item, str):
                    items.append(item)
                elif isinstance(item, list) and item:
                    items.append(str(item[0]))
            if items:
                return " ".join(items).replace("  ", " ").strip()
        elif isinstance(parsed, str):
            return parsed.strip()
        return str(parsed).strip()


def _translate_with_mymemory(text_clean: str, sl: str, tl: str) -> str:
    """
    Fallback sang MyMemory với cơ chế chia nhỏ câu nếu văn bản dài hơn 450 ký tự.
    """
    src_code = "vi-VN" if sl == "vi" else "en-GB"
    tgt_code = "en-GB" if tl == "en" else "vi-VN"
    translator = MyMemoryTranslator(source=src_code, target=tgt_code)

    if len(text_clean) <= 450:
        return translator.translate(text_clean)

    # Chia nhỏ văn bản theo từ sao cho mỗi phần < 400 ký tự
    words = text_clean.split(" ")
    chunks = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 > 400:
            if curr:
                chunks.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        chunks.append(" ".join(curr))

    results = []
    for c in chunks:
        try:
            res = translator.translate(c)
            results.append(res if res else c)
        except Exception:
            results.append(c)
    return " ".join(results)


def translate_text(text: str, source_lang: str = "vi", target_lang: str = "en") -> str:
    """
    Dịch văn bản giữa Tiếng Việt và Tiếng Anh với đa tầng fallback:
    1. Memory Cache (0ms)
    2. Google Translate Client endpoint POST (<300ms, hỗ trợ prompt dài)
    3. MyMemoryTranslator chunked fallback
    """
    text_clean = text.strip()
    if not text_clean:
        return ""
        
    cache_key = (text_clean, source_lang, target_lang)
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    sl = "vi" if source_lang.startswith("vi") else "en"
    tl = "en" if target_lang.startswith("en") else "vi"

    # Thử Google Translate endpoint trước (nhanh và chính xác)
    try:
        translated = _google_translate_fast(text_clean, sl, tl)
        if translated:
            _TRANSLATION_CACHE[cache_key] = translated
            return translated
    except Exception:
        pass

    # Fallback sang MyMemory (chia nhỏ an toàn nếu text dài)
    try:
        translated = _translate_with_mymemory(text_clean, sl, tl)
        if translated:
            _TRANSLATION_CACHE[cache_key] = translated
            return translated
    except Exception:
        pass

    return text_clean
