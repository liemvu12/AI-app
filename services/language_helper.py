"""
Trợ lý Ngôn ngữ Lập trình (Dev English Language Helper)
Kết hợp sửa lỗi ngữ pháp tiếng Anh (Grammar Checker) và chuẩn hoá phong cách kỹ thuật (Engineering Polish).
"""
import re
from .translator import detect_language, translate_text
from .grammar_checker import check_and_correct_grammar

# Bộ từ điển chuẩn hoá các cách diễn đạt thông thường sang Engineering English Cấp độ Pro Max
DEV_POLISH_REPLACEMENTS = [
    (r"\bfix this bug\b", "debug and resolve this issue"),
    (r"\bfix this error\b", "diagnose and fix this runtime error"),
    (r"\bmake it faster\b", "optimize execution performance and lower latency"),
    (r"\bwrite a code for\b", "implement a clean, production-grade routine for"),
    (r"\bwrite a code\b", "implement clean, modular, and maintainable code"),
    (r"\bhow to make\b", "how to architect and implement"),
    (r"\bchange this code\b", "refactor this implementation following clean code principles"),
    (r"\bcheck this error\b", "diagnose the root cause of this error"),
    (r"\brun this\b", "execute this routine"),
    (r"\bconnect to db\b", "configure and establish a resilient database connection pool"),
    (r"\bhandle error\b", "implement robust exception handling with fallback guards"),
    (r"\bmake it secure\b", "harden security and eliminate potential vulnerability vectors"),
    (r"\btest this\b", "design automated unit and integration tests with edge-case coverage"),
    (r"\bexplain this\b", "break down the architectural flow and algorithmic complexity of this"),
    (r"\bclean this\b", "refactor for clarity, modularity, and adherence to SOLID principles"),
    (r"\badd log\b", "instrument structured logging and telemetry for observability"),
]


def polish_engineering_english(text: str) -> str:
    """
    Nâng cấp câu lệnh tiếng Anh thông thường sang văn phong kỹ thuật chuẩn (Engineering Dev Polish).
    """
    polished = text.strip()
    if polished and polished[0].islower():
        polished = polished[0].upper() + polished[1:]
        
    for pattern, replacement in DEV_POLISH_REPLACEMENTS:
        polished = re.sub(pattern, replacement, polished, flags=re.IGNORECASE)
        
    return polished


def process_prompt_for_learning(prompt: str) -> dict:
    """
    Xử lý prompt đầu vào:
    - Nếu là Slash Command: Nhận diện lệnh Terminal ngay lập tức.
    - Nếu có Ollama: Gửi sang Ollama dịch hoặc sửa ngữ pháp.
    - Nếu không có Ollama (Fallback): Dịch MyMemory hoặc sửa bằng Regex & LanguageTool.
    """
    prompt = prompt.strip()
    if not prompt:
        return {
            "lang": "empty",
            "is_command": False,
            "original": "",
            "english_version": "",
            "grammar_fixed": "",
            "grammar_notes": [],
            "badge": "IDLE",
            "explanation": "Chờ prompt..."
        }

    # 1. Kiểm tra Slash command
    if prompt.startswith("/"):
        return {
            "lang": "command",
            "is_command": True,
            "original": prompt,
            "english_version": prompt,
            "grammar_fixed": prompt,
            "grammar_notes": [],
            "badge": "[TERMINAL COMMAND]",
            "explanation": "Lệnh điều khiển AGY Terminal (Không cần dịch)."
        }

    lang = detect_language(prompt)
    
    from .ollama_client import is_ollama_running, generate_text
    
    # 2. Xử lý qua AI Cục bộ (Ollama)
    if is_ollama_running():
        try:
            if lang == "vi":
                system_prompt = "You are a Senior Software Engineer. Translate the following Vietnamese text into concise, professional Engineering English command or sentence. Output ONLY the translated text, no markdown, no quotes, no explanations."
                polished_en = generate_text(prompt, system_prompt)
                # Cleanup potential quotes from LLM
                polished_en = polished_en.strip('"').strip("'")
                return {
                    "lang": "vi",
                    "is_command": False,
                    "original": prompt,
                    "english_version": polished_en,
                    "grammar_fixed": prompt,
                    "grammar_notes": ["Translated by Local AI"],
                    "badge": "[VI ➔ EN DEV TRANSLATION]",
                    "explanation": "Bản dịch tiếng Anh kỹ thuật (Ollama Local AI)."
                }
            else:
                system_prompt = "You are an English Grammar checker for developers. Fix any grammar mistakes in the user's input and polish it to sound like a native Senior Developer. If there are no errors, just return the polished version. Output ONLY the fixed text, no markdown, no quotes, no explanations."
                polished_en = generate_text(prompt, system_prompt)
                polished_en = polished_en.strip('"').strip("'")
                has_error = (polished_en.strip().lower() != prompt.strip().lower())
                return {
                    "lang": "en",
                    "is_command": False,
                    "original": prompt,
                    "grammar_fixed": polished_en,
                    "grammar_notes": ["Polished by Local AI"] if has_error else [],
                    "english_version": polished_en,
                    "badge": "[EN GRAMMAR & DEV POLISH]" if has_error else "[EN DEV POLISH]",
                    "has_grammar_error": has_error,
                    "explanation": "Đã tối ưu ngữ pháp bởi Ollama Local AI." if has_error else "Ngữ pháp chuẩn (Ollama Local AI)."
                }
        except Exception:
            pass # Fallback to old system if Ollama API fails

    # 3. Fallback Hệ thống cũ
    if lang == "vi":
        # Dịch câu tiếng Việt sang tiếng Anh
        raw_en = translate_text(prompt, source_lang="vi", target_lang="en")
        polished_en = polish_engineering_english(raw_en)
        return {
            "lang": "vi",
            "is_command": False,
            "original": prompt,
            "english_version": polished_en,
            "grammar_fixed": raw_en,
            "grammar_notes": [],
            "badge": "[VI ➔ EN DEV TRANSLATION]",
            "explanation": "Bản dịch tiếng Anh kỹ thuật (Dự phòng)."
        }
    else:
        # Nếu nhập tiếng Anh -> SỬA LỖI NGỮ PHÁP & CÚ PHÁP
        grammar_fixed, grammar_notes = check_and_correct_grammar(prompt)
        polished_en = polish_engineering_english(grammar_fixed)
        has_error = (grammar_fixed.strip().lower() != prompt.strip().lower())

        if has_error:
            explanation = "Phát hiện và đã sửa lỗi ngữ pháp / cú pháp tiếng Anh (Dự phòng)."
        else:
            explanation = "Ngữ pháp tiếng Anh chuẩn xác."

        return {
            "lang": "en",
            "is_command": False,
            "original": prompt,
            "grammar_fixed": grammar_fixed,
            "grammar_notes": grammar_notes,
            "english_version": polished_en,
            "badge": "[EN GRAMMAR & DEV POLISH]" if has_error else "[EN DEV POLISH]",
            "has_grammar_error": has_error,
            "explanation": explanation
        }
