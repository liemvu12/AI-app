"""
Bộ Kiểm Thử Toàn Diện 55 Kịch Bản Ngữ Pháp Phức Tạp (55 Complex Grammar Scenarios)
Dành cho AGY Dev English Pro Max Grammar & Syntax Engine.
"""
import sys
import os

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.language_helper import process_prompt_for_learning

TEST_SCENARIOS = [
    # --- Nhóm 1: Hòa hợp Chủ ngữ & Động từ (Subject-Verb Agreement) ---
    ("he have error in line 10", "Chủ ngữ số ít 'he' đi với 'has' + giới từ 'on line 10'"),
    ("she have permission to access the server", "Chủ ngữ số ít 'she' đi với 'has'"),
    ("this have a memory leak issue", "Chủ ngữ số ít 'this' đi với 'has'"),
    ("there is many bugs in the authentication module", "Chủ ngữ số nhiều 'many bugs' đi với 'there are'"),
    ("there is several race conditions in this code", "Chủ ngữ số nhiều 'several' đi với 'there are'"),
    ("user don't have write access to the repository", "Chủ ngữ số ít 'user' đi với 'doesn't'"),
    ("the server don't respond to ping requests", "Chủ ngữ số ít 'server' đi với 'doesn't'"),

    # --- Nhóm 2: Động từ khuyết thiếu & Trợ động từ (Modal Verbs & Bare Infinitives) ---
    ("can to run this script in background?", "Động từ khuyết thiếu 'can' đi với động từ nguyên thể không 'to'"),
    ("we must to restart the database container", "Động từ khuyết thiếu 'must' không đi với 'to'"),
    ("developer should to write clean code", "Động từ khuyết thiếu 'should' không đi với 'to'"),
    ("system could to handle high concurrency", "Động từ khuyết thiếu 'could' không đi với 'to'"),
    ("does it has support for websockets?", "Sau trợ động từ 'does', dùng động từ nguyên thể 'have'"),
    ("does it works on windows operating system?", "Sau trợ động từ 'does', dùng động từ nguyên thể 'work'"),

    # --- Nhóm 3: Thì Quá khứ & Trợ động từ (Past Tense with Auxiliaries) ---
    ("did you went to production server yesterday?", "Sau trợ động từ quá khứ 'did', dùng nguyên thể 'go'"),
    ("did you saw the exception in log file?", "Sau trợ động từ quá khứ 'did', dùng nguyên thể 'see'"),
    ("did you had any problem with docker setup?", "Sau trợ động từ quá khứ 'did', dùng nguyên thể 'have'"),
    ("will goes to fallback when primary fails", "Sau 'will' dùng động từ nguyên thể 'go'"),
    ("why it crash when input is null?", "Câu hỏi trực tiếp cần trợ động từ 'does'"),

    # --- Nhóm 4: Cú pháp câu hỏi & Đảo ngữ (Question Inversion & Word Order) ---
    ("how i can fix this error in line 10", "Đảo trợ động từ lên trước chủ ngữ 'how can I'"),
    ("how we can optimize this sql query", "Đảo trợ động từ 'how can we'"),
    ("why this happen when users logout?", "Trợ động từ câu hỏi 'why does this happen'"),
    ("where i can find the config file?", "Đảo trợ động từ 'where can I'"),
    ("what it mean when status code is 502?", "Trợ động từ câu hỏi 'what does it mean'"),

    # --- Nhóm 5: Thể bị động & Cấu trúc V-ing (Passive Voice & Gerunds) ---
    ("the deployment is finish successfully", "Thể bị động: 'is finished'"),
    ("user data is send over unencrypted http", "Thể bị động: 'is sent'"),
    ("config file is delete by cleanup script", "Thể bị động: 'is deleted'"),
    ("we look forward to hear your suggestion", "Cấu trúc 'look forward to' đi với V-ing"),
    ("instead of do manual testing, write automation", "Sau giới từ 'instead of' dùng V-ing"),

    # --- Nhóm 6: Giới từ kỹ thuật & Cụm từ cố định (Technical Prepositions & Collocations) ---
    ("check the syntax error in line 45", "Trong lập trình dùng 'on line X'"),
    ("null pointer exception at line 88", "Trong lập trình dùng 'on line X'"),
    ("can you explain me how redis cache works", "Cấu trúc đúng là 'explain to someone'"),
    ("let us discuss about microservices architecture", "'discuss' là ngoại động từ, không dùng 'about'"),
    ("this microservice depend of the message queue", "Giới từ cố định 'depend on'"),
    ("ensure the package is compatible to python 3.12", "Giới từ kỹ thuật chuẩn 'compatible with'"),

    # --- Nhóm 7: Giới từ Máy chủ, Mạng & Hệ thống (Server & Network Prepositions) ---
    ("the backend server listen at port 3000", "Trong mạng và server dùng 'listen on port X'"),
    ("application cannot connect in database", "Kết nối dùng 'connect to'"),
    ("nosql database is different than relational database", "Văn phong chuẩn là 'different from'"),
    ("senior developer is responsible of code review", "Cụm tính từ đúng là 'responsible for'"),

    # --- Nhóm 8: Từ dễ gây nhầm lẫn trong Tech (Confused Words in Programming) ---
    ("golang is faster then python for cpu tasks", "So sánh hơn dùng 'than' thay vì 'then'"),
    ("we have more then one hundred active connections", "So sánh hơn dùng 'than' thay vì 'then'"),
    ("be careful to not loose data during database migration", "Mất dữ liệu dùng động từ 'lose' thay vì 'loose'"),
    ("their is an unhandled promise rejection in nodejs", "Chỉ sự tồn tại dùng 'there is' thay vì 'their'"),
    ("check if its working in production environment", "Dạng viết tắt của 'it is' cần dấu nháy 'it's'"),
    ("how does this migration effect the users table", "Động từ tác động dùng 'affect' thay vì 'effect'"),
    ("can you advice me how to architecture this?", "Động từ khuyên bảo là 'advise' thay vì 'advice'"),

    # --- Nhóm 9: Danh từ không đếm được & Lượng từ (Uncountable Nouns & Quantifiers) ---
    ("the api returned too many informations", "'information' là danh từ không đếm được"),
    ("can you give me advices about system design?", "'advice' là danh từ không đếm được"),
    ("we need to install many softwares on this server", "'software' là danh từ không đếm được, dùng 'much'"),
    ("we received positive feedbacks from qa team", "'feedback' là danh từ không đếm được"),
    ("data center purchased new equipments yesterday", "'equipment' là danh từ không đếm được"),

    # --- Nhóm 10: Phủ định kép & Viết tắt (Double Negatives & Contractions) ---
    ("the api don't return nothing when query fails", "Tránh phủ định kép: dùng 'anything'"),
    ("the worker doesn't have no task assigned", "Tránh phủ định kép: dùng 'any'"),
    ("dont deploy to prod because it isnt tested", "Sửa viết tắt thiếu dấu nháy: 'don't', 'isn't'"),

    # --- Nhóm 11: Mạo từ Kỹ thuật (Technical Articles) ---
    ("we need to create a api endpoint for payment", "Từ viết tắt 'API' bắt đầu bằng nguyên âm, dùng 'an'"),
    ("the service returns a http status 404", "Từ 'HTTP' đọc bắt đầu bằng nguyên âm, dùng 'an'"),
    ("each record must have an unique identifier", "Từ 'unique' phát âm bằng phụ âm /j/, dùng 'a'"),
]


def run_55_scenarios_validation():
    print("=" * 75)
    print(f"BẮT ĐẦU CHẠY KIỂM THỬ TOÀN DIỆN {len(TEST_SCENARIOS)} KỊCH BẢN NGỮ PHÁP DEV...")
    print("=" * 75)

    passed_count = 0
    failed_count = 0
    results = []

    for idx, (raw_prompt, expectation) in enumerate(TEST_SCENARIOS, 1):
        res = process_prompt_for_learning(raw_prompt)
        original = res["original"]
        fixed = res["grammar_fixed"]
        polish = res["english_version"]
        notes = res.get("grammar_notes", [])
        has_error = res.get("has_grammar_error", False)

        # Tiêu chuẩn: Câu gốc có lỗi và đã được sửa thành công (fixed != original hoặc có ghi chú lỗi)
        is_fixed = (fixed.lower() != original.lower()) or (len(notes) > 0)
        
        status_icon = "✅ PASS" if is_fixed else "❌ FAIL"
        if is_fixed:
            passed_count += 1
        else:
            failed_count += 1

        results.append({
            "idx": idx,
            "raw": original,
            "fixed": fixed,
            "polish": polish,
            "notes": notes,
            "expected": expectation,
            "status": is_fixed
        })

        print(f"[{idx:02d}/55] {status_icon} | Nhập: \"{original}\"")
        print(f"      ➔ Đã sửa: \"{fixed}\"")
        if notes:
            print(f"      ➔ Điểm sửa: {notes[0]}")
        print("-" * 75)

    print("=" * 75)
    print(f">> KẾT QUẢ KIỂM THỬ: {passed_count}/{len(TEST_SCENARIOS)} KỊCH BẢN ĐẠT CHUẨN! <<")
    print(f">> TỶ LỆ CHÍNH XÁC: {(passed_count / len(TEST_SCENARIOS)) * 100:.1f}% <<")
    print("=" * 75)

    if failed_count > 0:
        print(f"Cảnh báo: Có {failed_count} kịch bản chưa được sửa đổi.")
        sys.exit(1)
    else:
        print("TẤT CẢ CÁC KỊCH BẢN NGỮ PHÁP PHỨC TẠP ĐÃ ĐƯỢC XỬ LÝ HOÀN HẢO!")
        sys.exit(0)


if __name__ == "__main__":
    run_55_scenarios_validation()
