"""
Hệ thống Kiểm tra & Sửa lỗi Ngữ pháp Tiếng Anh Cấp độ Pro Max ULTRA
(Pro Max ULTRA English Grammar & Dev Syntax Engine)
Kiến trúc 3 Tầng Siêu Cấp:
1. Tầng tức thì (0ms - Offline): 165+ quy tắc ngữ pháp chuyên sâu cho lập trình viên.
   - Hòa hợp chủ vị, trợ động từ, thì động từ (Tense), mệnh đề quan hệ (Relative Clauses),
     câu điều kiện (Conditionals), giới từ kỹ thuật, từ dễ nhầm, collocation, mạo từ.
2. Tầng phân tích chuyên sâu (Deep NLP): LanguageTool REST Engine + whitelist 160+ thuật ngữ tech.
3. Tầng Từ vựng Nâng cao (Vocabulary Enrichment): Gợi ý thay thế từ vựng Engineering chuẩn cao cấp.
"""
import urllib.request
import urllib.parse
import json
import re
from typing import Tuple

_GRAMMAR_CACHE: dict[str, Tuple[str, list[str]]] = {}

# BỘ QUY TẮC NGỮ PHÁP DEV CHUYÊN SÂU (TỨC THÌ 0MS - OFFLINE FIRST)
# Cấu trúc mỗi rule: (pattern, replacement, category, explanation)
PRO_MAX_GRAMMAR_RULES = [
    # =========================================================
    # --- 1. Hòa hợp Chủ ngữ & Động từ (Subject-Verb Agreement) ---
    # =========================================================
    (r"\bhe have\b", "he has", "Ngữ pháp", "Chủ ngữ 'he' đi với động từ số ít 'has' thay vì 'have'"),
    (r"\bshe have\b", "she has", "Ngữ pháp", "Chủ ngữ 'she' đi với động từ số ít 'has' thay vì 'have'"),
    (r"\bit have\b", "it has", "Ngữ pháp", "Chủ ngữ 'it' đi với động từ số ít 'has' thay vì 'have'"),
    (r"\bthis have\b", "this has", "Ngữ pháp", "Chủ ngữ số ít 'this' đi với 'has'"),
    (r"\bthat have\b", "that has", "Ngữ pháp", "Chủ ngữ số ít 'that' đi với 'has'"),
    (r"\bhow it work\b", "how it works", "Ngữ pháp", "Chủ ngữ số ít 'it' đi với động từ thêm 's' ('works')"),
    (r"\bwhy it have\b", "why it has", "Ngữ pháp", "Chủ ngữ 'it' đi với 'has' thay vì 'have'"),
    (r"\bthere is many\b", "there are many", "Ngữ pháp", "Chủ ngữ số nhiều 'many' bắt buộc đi với 'there are'"),
    (r"\bthere is several\b", "there are several", "Ngữ pháp", "Chủ ngữ số nhiều 'several' đi với 'there are'"),
    (r"\bthere is a lot of bugs\b", "there are a lot of bugs", "Ngữ pháp", "Danh từ đếm được số nhiều 'bugs' đi với 'there are'"),
    (r"\buser don't have\b", "user doesn't have", "Ngữ pháp", "Chủ ngữ số ít 'user' đi với 'doesn't'"),
    (r"\bserver don't\b", "server doesn't", "Ngữ pháp", "Chủ ngữ số ít 'server' đi với 'doesn't'"),
    (r"\bthe system don't\b", "the system doesn't", "Ngữ pháp", "Chủ ngữ số ít 'system' đi với 'doesn't'"),
    (r"\bthe app don't\b", "the app doesn't", "Ngữ pháp", "Chủ ngữ số ít 'app' đi với 'doesn't'"),
    (r"\bthe function don't\b", "the function doesn't", "Ngữ pháp", "Chủ ngữ số ít 'function' đi với 'doesn't'"),
    (r"\bthe api don't\b", "the api doesn't", "Ngữ pháp", "Chủ ngữ số ít 'api' đi với 'doesn't'"),
    (r"\bthe code don't\b", "the code doesn't", "Ngữ pháp", "Chủ ngữ số ít 'code' đi với 'doesn't'"),
    (r"\bthere is (multiple|numerous|various)\b", r"there are \1", "Ngữ pháp", "Số nhiều bắt buộc dùng 'there are'"),

    # =========================================================
    # --- 2. Trợ động từ & Động từ khuyết thiếu (Auxiliary & Modal Verbs) ---
    # =========================================================
    (r"\bcan to ([a-z]+)\b", r"can \1", "Ngữ pháp", "Động từ khuyết thiếu 'can' đi với động từ nguyên thể không 'to'"),
    (r"\bmust to ([a-z]+)\b", r"must \1", "Ngữ pháp", "Động từ khuyết thiếu 'must' đi với động từ nguyên thể không 'to'"),
    (r"\bshould to ([a-z]+)\b", r"should \1", "Ngữ pháp", "Động từ khuyết thiếu 'should' đi với động từ nguyên thể không 'to'"),
    (r"\bcould to ([a-z]+)\b", r"could \1", "Ngữ pháp", "Động từ khuyết thiếu 'could' đi với động từ nguyên thể không 'to'"),
    (r"\bwould to ([a-z]+)\b", r"would \1", "Ngữ pháp", "Động từ khuyết thiếu 'would' đi với động từ nguyên thể không 'to'"),
    (r"\bmight to ([a-z]+)\b", r"might \1", "Ngữ pháp", "Động từ khuyết thiếu 'might' đi với động từ nguyên thể không 'to'"),
    (r"\bdoes it has\b", "does it have", "Ngữ pháp", "Sau trợ động từ 'does', dùng động từ nguyên thể 'have'"),
    (r"\bdoes it works\b", "does it work", "Ngữ pháp", "Sau trợ động từ 'does', dùng động từ nguyên thể 'work'"),
    (r"\bdoes it runs\b", "does it run", "Ngữ pháp", "Sau trợ động từ 'does', dùng động từ nguyên thể 'run'"),
    (r"\bdoes it returns\b", "does it return", "Ngữ pháp", "Sau trợ động từ 'does', dùng động từ nguyên thể 'return'"),
    (r"\bdoes it supports\b", "does it support", "Ngữ pháp", "Sau trợ động từ 'does', dùng động từ nguyên thể 'support'"),
    (r"\bdid you went\b", "did you go", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'go'"),
    (r"\bdid you saw\b", "did you see", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'see'"),
    (r"\bdid you had\b", "did you have", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'have'"),
    (r"\bdid you made\b", "did you make", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'make'"),
    (r"\bdid you wrote\b", "did you write", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'write'"),
    (r"\bdid you ran\b", "did you run", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'run'"),
    (r"\bdid you deployed\b", "did you deploy", "Ngữ pháp", "Sau trợ động từ quá khứ 'did', dùng động từ nguyên thể 'deploy'"),
    (r"\bwill goes\b", "will go", "Ngữ pháp", "Sau 'will' dùng động từ nguyên thể 'go'"),
    (r"\bwill returns\b", "will return", "Ngữ pháp", "Sau 'will' dùng động từ nguyên thể 'return'"),
    (r"\bwill runs\b", "will run", "Ngữ pháp", "Sau 'will' dùng động từ nguyên thể 'run'"),
    (r"\bwill starts\b", "will start", "Ngữ pháp", "Sau 'will' dùng động từ nguyên thể 'start'"),

    # =========================================================
    # --- 3. THÌ ĐỘNG TỪ (TENSE CONSISTENCY) - MỚI ---
    # =========================================================
    # 3a. Thì hiện tại tiếp diễn (am/is/are + V-bare → am/is/are + V-ing)
    (r"\bi am work\b", "I am working", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'am working' (am + V-ing)"),
    (r"\bhe is work\b", "he is working", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is working' (is + V-ing)"),
    (r"\bshe is work\b", "she is working", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is working' (is + V-ing)"),
    (r"\bit is run\b", "it is running", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is running' (is + V-ing)"),
    (r"\bthey are deploy\b", "they are deploying", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'are deploying' (are + V-ing)"),
    (r"\bwe are build\b", "we are building", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'are building' (are + V-ing)"),
    (r"\bi am try to\b", "I am trying to", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'am trying to'"),
    (r"\bhe is try to\b", "he is trying to", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is trying to'"),
    (r"\bthe system is process\b", "the system is processing", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is processing'"),
    (r"\bthe server is listen\b", "the server is listening", "Ngữ pháp", "Thì hiện tại tiếp diễn: 'is listening'"),
    # 3b. Trạng từ quá khứ + thì hiện tại (lỗi phổ biến)
    (r"\byesterday i (?:go|goes)\b", "yesterday I went", "Ngữ pháp", "Trạng từ 'yesterday' → thì quá khứ đơn 'went'"),
    (r"\byesterday (he|she|it) (?:go|goes)\b", r"yesterday \1 went", "Ngữ pháp", "Trạng từ 'yesterday' → thì quá khứ đơn"),
    (r"\blast week i (?:push|pushes)\b", "last week I pushed", "Ngữ pháp", "Trạng từ 'last week' → 'pushed' (quá khứ đơn)"),
    (r"\blast night (?:the system|it|the server) (?:crash|crashes)\b", "last night the system crashed", "Ngữ pháp", "Trạng từ 'last night' → thì quá khứ đơn"),
    # 3c. Thì hiện tại hoàn thành (have/has + V3)
    (r"\bi have finish\b", "I have finished", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have finished' (have + V3)"),
    (r"\bhe has finish\b", "he has finished", "Ngữ pháp", "Thì hiện tại hoàn thành: 'has finished' (has + V3)"),
    (r"\bwe have deploy\b", "we have deployed", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have deployed' (have + V3)"),
    (r"\bi have already push\b", "I have already pushed", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have already pushed'"),
    (r"\bshe has already write\b", "she has already written", "Ngữ pháp", "Thì hiện tại hoàn thành: 'has already written'"),
    (r"\bthey have implement\b", "they have implemented", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have implemented'"),
    (r"\bwe have test\b", "we have tested", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have tested'"),
    (r"\bwe have already commit\b", "we have already committed", "Ngữ pháp", "Thì hiện tại hoàn thành: 'have already committed'"),
    # 3d. Lỗi kết hợp trạng từ thời gian + thì sai
    (r"\bsince (\d+) year ago\b", r"for \1 years", "Ngữ pháp", "'since' chỉ thời điểm cụ thể; dùng 'for' cho khoảng thời gian"),
    (r"\bfor (\d+) years ago\b", r"\1 years ago", "Ngữ pháp", "'ago' theo sau khoảng thời gian, không kết hợp với 'for'"),

    # =========================================================
    # --- 4. Thể bị động & Cấu trúc V-ing (Passive Voice & Gerunds) ---
    # =========================================================
    (r"\blook forward to hear\b", "look forward to hearing", "Ngữ pháp", "Cấu trúc 'look forward to' đi với danh động từ V-ing"),
    (r"\binstead of do\b", "instead of doing", "Ngữ pháp", "Sau giới từ 'instead of' dùng V-ing"),
    (r"\bprevent from do\b", "prevent from doing", "Ngữ pháp", "Sau giới từ 'from' dùng V-ing"),
    (r"\bit is finish\b", "it is finished", "Ngữ pháp", "Thể bị động: 'is finished'"),
    (r"\bdata is send\b", "data is sent", "Ngữ pháp", "Thể bị động: 'is sent'"),
    (r"\bfile is delete\b", "file is deleted", "Ngữ pháp", "Thể bị động: 'is deleted'"),
    (r"\bcode is push\b", "code is pushed", "Ngữ pháp", "Thể bị động: 'is pushed'"),
    (r"\btoken is expire\b", "token is expired", "Ngữ pháp", "Thể bị động: 'is expired'"),
    (r"\bcache is clear\b", "cache is cleared", "Ngữ pháp", "Thể bị động: 'is cleared'"),
    (r"\bqueue is process\b", "queue is processed", "Ngữ pháp", "Thể bị động: 'is processed'"),
    (r"\bthe request is reject\b", "the request is rejected", "Ngữ pháp", "Thể bị động: 'is rejected'"),
    (r"\bthe data was send\b", "the data was sent", "Ngữ pháp", "Thể bị động quá khứ: 'was sent'"),
    # V-ing sau giới từ
    (r"\bwithout test\b", "without testing", "Ngữ pháp", "Sau giới từ 'without' dùng V-ing: 'without testing'"),
    (r"\bby use\b", "by using", "Ngữ pháp", "Sau giới từ 'by' dùng V-ing: 'by using'"),
    (r"\bfor avoid\b", "for avoiding", "Ngữ pháp", "Sau giới từ 'for' dùng V-ing: 'for avoiding'"),
    (r"\bbefore deploy\b", "before deploying", "Ngữ pháp", "Sau giới từ 'before' dùng V-ing: 'before deploying'"),
    (r"\bafter commit\b", "after committing", "Ngữ pháp", "Sau giới từ 'after' dùng V-ing: 'after committing'"),
    (r"\bconsider to use\b", "consider using", "Ngữ pháp", "Động từ 'consider' đi với V-ing, không phải 'to + V'"),
    (r"\bavoid to use\b", "avoid using", "Ngữ pháp", "Động từ 'avoid' đi với V-ing, không phải 'to + V'"),
    (r"\brecommend to use\b", "recommend using", "Ngữ pháp", "Động từ 'recommend' đi với V-ing, không phải 'to + V'"),

    # =========================================================
    # --- 5. Trật tự từ trong câu hỏi & Đảo ngữ (Question Inversion) ---
    # =========================================================
    (r"\bhow i can\b", "how can I", "Cú pháp", "Câu hỏi: đảo trợ động từ lên trước chủ ngữ → 'how can I'"),
    (r"\bhow we can\b", "how can we", "Cú pháp", "Câu hỏi: đảo trợ động từ → 'how can we'"),
    (r"\bwhy this happen\b", "why does this happen", "Cú pháp", "Câu hỏi cần trợ động từ 'does' → 'why does this happen'"),
    (r"\bwhy it crash\b", "why does it crash", "Cú pháp", "Câu hỏi cần trợ động từ 'does' → 'why does it crash'"),
    (r"\bwhere i can\b", "where can I", "Cú pháp", "Câu hỏi: đảo trợ động từ → 'where can I'"),
    (r"\bwhen it will\b", "when will it", "Cú pháp", "Câu hỏi: đảo 'will' lên trước chủ ngữ → 'when will it'"),
    (r"\bwhat it mean\b", "what does it mean", "Cú pháp", "Câu hỏi cần trợ động từ 'does' → 'what does it mean'"),
    (r"\bhow it works\?", "how does it work?", "Cú pháp", "Câu hỏi trực tiếp cần trợ động từ 'does'"),
    (r"\bwhat it return\b", "what does it return", "Cú pháp", "Câu hỏi cần trợ động từ 'does' → 'what does it return'"),
    (r"\bwhy the test fail\b", "why does the test fail", "Cú pháp", "Câu hỏi cần trợ động từ 'does'"),
    (r"\bhow the system work\b", "how does the system work", "Cú pháp", "Câu hỏi cần trợ động từ 'does'"),
    (r"\bwhat this function do\b", "what does this function do", "Cú pháp", "Câu hỏi cần trợ động từ 'does'"),
    (r"\bwhere it store\b", "where does it store", "Cú pháp", "Câu hỏi cần trợ động từ 'does'"),
    (r"\bwho i should\b", "who should I", "Cú pháp", "Câu hỏi với 'who': đảo trợ động từ → 'who should I'"),

    # =========================================================
    # --- 6. MỆNH ĐỀ QUAN HỆ (RELATIVE CLAUSES) - MỚI ---
    # =========================================================
    # Bỏ đại từ thừa sau từ quan hệ
    (r"\bthat it (is|was|has|have|can|will|should)\b", r"that \1", "Cú pháp", "Mệnh đề quan hệ: bỏ đại từ 'it' thừa sau 'that'"),
    (r"\bwhich it (is|was|has|have|can|will|returns?|runs?|works?)\b", r"which \1", "Cú pháp", "Mệnh đề quan hệ: bỏ đại từ 'it' thừa sau 'which'"),
    (r"\bwho he (is|was|has|have|can|will|said)\b", r"who \1", "Cú pháp", "Mệnh đề quan hệ: bỏ đại từ 'he' thừa sau 'who'"),
    (r"\bwho she (is|was|has|have|can|will|said)\b", r"who \1", "Cú pháp", "Mệnh đề quan hệ: bỏ đại từ 'she' thừa sau 'who'"),
    (r"\bthe function which it returns\b", "the function that returns", "Cú pháp", "Mệnh đề quan hệ: bỏ đại từ 'it' thừa"),
    (r"\bthe user that he created\b", "the user who created", "Cú pháp", "Dùng 'who' cho người và bỏ đại từ 'he' thừa"),
    (r"\bthe developer that he wrote\b", "the developer who wrote", "Cú pháp", "Dùng 'who' cho người, bỏ 'he' thừa"),
    # Dùng đúng who/which/that
    (r"\bthe person which\b", "the person who", "Cú pháp", "Dùng 'who' (không phải 'which') cho người"),
    (r"\bthe developer which\b", "the developer who", "Cú pháp", "Dùng 'who' (không phải 'which') cho người"),
    (r"\bthe engineer which\b", "the engineer who", "Cú pháp", "Dùng 'who' (không phải 'which') cho người"),
    # Động từ nội động từ không dùng bị động
    (r"\bthat was occurred\b", "that occurred", "Ngữ pháp", "'occur' là nội động từ, không dùng bị động 'was occurred'"),
    (r"\bthat was happened\b", "that happened", "Ngữ pháp", "'happen' là nội động từ, không dùng bị động 'was happened'"),
    (r"\bthat was appeared\b", "that appeared", "Ngữ pháp", "'appear' là nội động từ, không dùng bị động 'was appeared'"),
    (r"\bwhich was occurred\b", "which occurred", "Ngữ pháp", "'occur' là nội động từ, không dùng bị động 'was occurred'"),

    # =========================================================
    # --- 7. CÂU ĐIỀU KIỆN (CONDITIONAL SENTENCES) - MỚI ---
    # =========================================================
    # Type 1: if + present → will + V (không dùng 'would' ở mệnh đề if)
    (r"\bif it would work\b", "if it works", "Ngữ pháp", "Câu điều kiện loại 1: mệnh đề 'if' dùng thì hiện tại, không dùng 'would'"),
    (r"\bif the server would crash\b", "if the server crashes", "Ngữ pháp", "Câu điều kiện loại 1: 'if' dùng thì hiện tại đơn"),
    (r"\bif the test would pass\b", "if the test passes", "Ngữ pháp", "Câu điều kiện loại 1: 'if' dùng thì hiện tại đơn"),
    (r"\bif it would fail\b", "if it fails", "Ngữ pháp", "Câu điều kiện loại 1: 'if' dùng thì hiện tại đơn 'fails'"),
    # Type 2: if + past simple → would + V (subjunctive mood)
    (r"\bif i would know\b", "if I knew", "Ngữ pháp", "Câu điều kiện loại 2: 'if I knew' (past subjunctive)"),
    (r"\bif i would have access\b", "if I had access", "Ngữ pháp", "Câu điều kiện loại 2: 'if I had access'"),
    (r"\bif i would be\b", "if I were", "Ngữ pháp", "Câu điều kiện loại 2: 'if I were' (subjunctive mood)"),
    (r"\bif he would be\b", "if he were", "Ngữ pháp", "Câu điều kiện loại 2: 'if he were' (subjunctive mood)"),
    (r"\bif she would be\b", "if she were", "Ngữ pháp", "Câu điều kiện loại 2: 'if she were' (subjunctive mood)"),
    # Type 3: if + had + V3 → would have + V3
    (r"\bif (i|he|she|we|they) would have ([a-z]+ed)\b", r"if \1 had \2", "Ngữ pháp", "Câu điều kiện loại 3: dùng 'if + had + V3' ở mệnh đề điều kiện"),
    # Unless (tương đương if...not, không thêm 'not')
    (r"\bunless you not\b", "unless you", "Ngữ pháp", "'unless' đã có nghĩa phủ định, không thêm 'not'"),
    (r"\bunless it not\b", "unless it", "Ngữ pháp", "'unless' đã có nghĩa phủ định, không thêm 'not'"),
    (r"\bunless the server not\b", "unless the server", "Ngữ pháp", "'unless' tương đương 'if...not', không thêm 'not'"),
    (r"\bunless you don't\b", "unless you", "Ngữ pháp", "'unless' đã là phủ định, loại bỏ 'don't' thừa"),

    # =========================================================
    # --- 8. Giới từ kỹ thuật & Cụm cố định (Technical Prepositions & Collocations) ---
    # =========================================================
    (r"\bin line (\d+)\b", r"on line \1", "Giới từ", "Trong lập trình dùng 'on line X'"),
    (r"\bat line (\d+)\b", r"on line \1", "Giới từ", "Trong lập trình dùng 'on line X'"),
    (r"\bexplain me\b", "explain to me", "Cụm từ", "Cấu trúc đúng: 'explain to someone'"),
    (r"\bdiscuss about\b", "discuss", "Giới từ", "'discuss' là ngoại động từ, không dùng với 'about'"),
    (r"\bdepend of\b", "depend on", "Giới từ", "Giới từ đúng sau 'depend': 'on'"),
    (r"\bdepends of\b", "depends on", "Giới từ", "Giới từ đúng sau 'depends': 'on'"),
    (r"\bconsist in\b", "consist of", "Giới từ", "Giới từ đúng sau 'consist': 'of'"),
    (r"\bresponsible of\b", "responsible for", "Giới từ", "Cụm tính từ đúng: 'responsible for'"),
    (r"\bcompatible to\b", "compatible with", "Giới từ", "Giới từ kỹ thuật chuẩn: 'compatible with'"),
    (r"\blisten at port (\d+)\b", r"listen on port \1", "Giới từ", "Trong mạng/server dùng 'listen on port X'"),
    (r"\bconnect in database\b", "connect to database", "Giới từ", "Giới từ kết nối: 'connect to'"),
    (r"\bdifferent than\b", "different from", "Giới từ", "Văn phong kỹ thuật chuẩn: 'different from'"),
    (r"\binterested for\b", "interested in", "Giới từ", "Tính từ 'interested' đi với giới từ 'in'"),
    (r"\bby using of\b", "by using", "Cụm từ", "Lược bỏ 'of' thừa sau 'using'"),
    (r"\baccord to\b", "according to", "Cụm từ", "Cụm từ đúng: 'according to'"),
    (r"\bintegrate in\b", "integrate with", "Giới từ", "Giới từ đúng sau 'integrate': 'with'"),
    (r"\bintegrates in\b", "integrates with", "Giới từ", "Giới từ đúng sau 'integrates': 'with'"),
    (r"\bcollaborate in\b", "collaborate on", "Giới từ", "Giới từ đúng sau 'collaborate': 'on'"),
    (r"\bfocused in\b", "focused on", "Giới từ", "Tính từ 'focused' đi với giới từ 'on'"),
    (r"\bbased in the\b", "based on the", "Giới từ", "Cụm từ đúng: 'based on'"),
    (r"\bwait the response\b", "wait for the response", "Giới từ", "Giới từ đúng sau 'wait': 'for'"),
    (r"\bsearch the error\b", "search for the error", "Giới từ", "Giới từ đúng sau 'search': 'for'"),
    (r"\brun on background\b", "run in the background", "Giới từ", "Cụm từ đúng: 'run in the background'"),
    (r"\bin the other hand\b", "on the other hand", "Cụm từ", "Thành ngữ đúng: 'on the other hand'"),

    # =========================================================
    # --- 9. Các cặp từ dễ gây nhầm lẫn (Confused Words in Tech) ---
    # =========================================================
    (r"\bfaster then\b", "faster than", "Từ dễ nhầm", "So sánh hơn dùng 'than' thay vì 'then'"),
    (r"\bbetter then\b", "better than", "Từ dễ nhầm", "So sánh hơn dùng 'than' thay vì 'then'"),
    (r"\bmore then\b", "more than", "Từ dễ nhầm", "So sánh hơn dùng 'than' thay vì 'then'"),
    (r"\bless then\b", "less than", "Từ dễ nhầm", "So sánh hơn dùng 'than' thay vì 'then'"),
    (r"\bloose data\b", "lose data", "Từ dễ nhầm", "Mất dữ liệu: 'lose' (động từ), không phải 'loose' (tính từ)"),
    (r"\bloose memory\b", "lose memory", "Từ dễ nhầm", "Rò rỉ bộ nhớ: 'lose memory', không phải 'loose'"),
    (r"\btheir is\b", "there is", "Từ dễ nhầm", "Chỉ sự tồn tại: 'there is', không phải sở hữu 'their'"),
    (r"\btheir are\b", "there are", "Từ dễ nhầm", "Chỉ sự tồn tại: 'there are', không phải sở hữu 'their'"),
    (r"\bits working\b", "it's working", "Từ dễ nhầm", "Viết tắt 'it is': 'it's', cần dấu nháy đơn"),
    (r"\bit's value\b", "its value", "Từ dễ nhầm", "Tính từ sở hữu: 'its' (không có dấu nháy)"),
    (r"\bhow does this effect\b", "how does this affect", "Từ dễ nhầm", "Động từ: 'affect', không phải danh từ 'effect'"),
    (r"\bprincipal of\b", "principle of", "Từ dễ nhầm", "Nguyên lý thiết kế: 'principle', không phải 'principal'"),
    (r"\bcan you advice me\b", "can you advise me", "Từ dễ nhầm", "Động từ: 'advise', không phải danh từ 'advice'"),
    (r"\bsite effect\b", "side effect", "Từ dễ nhầm", "Thuật ngữ kỹ thuật đúng: 'side effect'"),
    (r"\bsite effects\b", "side effects", "Từ dễ nhầm", "Thuật ngữ kỹ thuật đúng: 'side effects'"),
    (r"\bpast the token\b", "pass the token", "Từ dễ nhầm", "Động từ 'pass' (truyền), không phải 'past' (quá khứ)"),
    (r"\bpast the data\b", "pass the data", "Từ dễ nhầm", "Động từ 'pass' (truyền dữ liệu), không phải 'past'"),
    (r"\ba complied binary\b", "a compiled binary", "Chính tả", "Từ đúng: 'compiled' (đã biên dịch)"),
    (r"\bcompose of\b", "composed of", "Từ dễ nhầm", "Cấu trúc bị động đúng: 'composed of'"),

    # =========================================================
    # --- 10. Danh từ không đếm được & Lượng từ ---
    # =========================================================
    (r"\binformations\b", "information", "Ngữ pháp", "'information' là danh từ không đếm được"),
    (r"\badvices\b", "advice", "Ngữ pháp", "'advice' là danh từ không đếm được"),
    (r"\bsoftwares\b", "software", "Ngữ pháp", "'software' là danh từ không đếm được"),
    (r"\bhardwares\b", "hardware", "Ngữ pháp", "'hardware' là danh từ không đếm được"),
    (r"\bfeedbacks\b", "feedback", "Ngữ pháp", "'feedback' là danh từ không đếm được"),
    (r"\bequipments\b", "equipment", "Ngữ pháp", "'equipment' là danh từ không đếm được"),
    (r"\bknowledges\b", "knowledge", "Ngữ pháp", "'knowledge' là danh từ không đếm được"),
    (r"\bresearches\b", "research", "Ngữ pháp", "'research' là danh từ không đếm được"),
    (r"\ba lots of\b", "a lot of", "Ngữ pháp", "Cụm lượng từ đúng: 'a lot of'"),
    (r"\bmany informations\b", "much information", "Ngữ pháp", "'information' không đếm được, dùng 'much'"),
    (r"\bmany softwares\b", "much software", "Ngữ pháp", "'software' không đếm được, dùng 'much'"),
    (r"\bmany datas\b", "much data", "Ngữ pháp", "'data' không đếm được trong kỹ thuật, dùng 'much'"),
    (r"\bbehaviours\b", "behavior", "Chính tả", "Văn phong kỹ thuật Mỹ chuẩn: 'behavior' (không có 'u')"),

    # =========================================================
    # --- 11. Phủ định kép & Viết tắt (Double Negatives & Contractions) ---
    # =========================================================
    (r"\bdon't know nothing\b", "don't know anything", "Ngữ pháp", "Tránh phủ định kép: 'anything' sau 'don't'"),
    (r"\bdoesn't have no\b", "doesn't have any", "Ngữ pháp", "Tránh phủ định kép: 'any' sau 'doesn't'"),
    (r"\bit dont\b", "it doesn't", "Ngữ pháp", "Chủ ngữ số ít 'it' đi với 'doesn't'"),
    (r"\bit doesnt\b", "it doesn't", "Chính tả", "Thiếu dấu nháy đơn trong 'doesn't'"),
    (r"\bhe dont\b", "he doesn't", "Ngữ pháp", "Chủ ngữ số ít 'he' đi với 'doesn't'"),
    (r"\bshe dont\b", "she doesn't", "Ngữ pháp", "Chủ ngữ số ít 'she' đi với 'doesn't'"),
    (r"\bdont\b", "don't", "Chính tả", "Thiếu dấu nháy đơn trong 'don't'"),
    (r"\bcant\b", "can't", "Chính tả", "Thiếu dấu nháy đơn trong 'can't'"),
    (r"\bwont\b", "won't", "Chính tả", "Thiếu dấu nháy đơn trong 'won't'"),
    (r"\bisnt\b", "isn't", "Chính tả", "Thiếu dấu nháy đơn trong 'isn't'"),
    (r"\barent\b", "aren't", "Chính tả", "Thiếu dấu nháy đơn trong 'aren't'"),
    (r"\bhasnt\b", "hasn't", "Chính tả", "Thiếu dấu nháy đơn trong 'hasn't'"),
    (r"\bhavent\b", "haven't", "Chính tả", "Thiếu dấu nháy đơn trong 'haven't'"),
    (r"\bwasnt\b", "wasn't", "Chính tả", "Thiếu dấu nháy đơn trong 'wasn't'"),
    (r"\bwerent\b", "weren't", "Chính tả", "Thiếu dấu nháy đơn trong 'weren't'"),
    (r"\bcouldnt\b", "couldn't", "Chính tả", "Thiếu dấu nháy đơn trong 'couldn't'"),
    (r"\bshouldnt\b", "shouldn't", "Chính tả", "Thiếu dấu nháy đơn trong 'shouldn't'"),
    (r"\bwouldnt\b", "wouldn't", "Chính tả", "Thiếu dấu nháy đơn trong 'wouldn't'"),

    # =========================================================
    # --- 12. Mạo từ kỹ thuật (Articles - Expanded) ---
    # =========================================================
    (r"\ban unique\b", "a unique", "Ngữ pháp", "Từ 'unique' phát âm bằng phụ âm /j/, dùng 'a'"),
    (r"\ba hour\b", "an hour", "Ngữ pháp", "'hour' phát âm bằng nguyên âm /aʊ/, dùng 'an'"),
    (r"\ba api\b", "an API", "Ngữ pháp", "Từ viết tắt 'API' đọc bắt đầu nguyên âm /eɪ/, dùng 'an'"),
    (r"\ba http\b", "an HTTP", "Ngữ pháp", "Từ 'HTTP' đọc bắt đầu nguyên âm /eɪtʃ/, dùng 'an'"),
    (r"\ba sql\b", "an SQL", "Ngữ pháp", "Từ viết tắt 'SQL' đọc là /ɛs/, dùng 'an'"),
    (r"\ba url\b", "a URL", "Ngữ pháp", "URL đọc là /juː/ (phụ âm /j/), dùng 'a'"),
    (r"\ban user\b", "a user", "Ngữ pháp", "Từ 'user' phát âm /j/ (phụ âm), dùng 'a user'"),
    (r"\ban uniform\b", "a uniform", "Ngữ pháp", "Từ 'uniform' phát âm /j/ (phụ âm), dùng 'a uniform'"),
    (r"\ba error\b", "an error", "Ngữ pháp", "Từ 'error' phát âm /ɛ/ (nguyên âm), dùng 'an error'"),
    (r"\ba exception\b", "an exception", "Ngữ pháp", "Từ 'exception' phát âm /ɛ/ (nguyên âm), dùng 'an exception'"),
    (r"\ba integer\b", "an integer", "Ngữ pháp", "Từ 'integer' phát âm /ɪ/ (nguyên âm), dùng 'an integer'"),
    (r"\ba enum\b", "an enum", "Ngữ pháp", "Từ 'enum' phát âm /ɛ/ (nguyên âm), dùng 'an enum'"),

    # =========================================================
    # --- 13. COLLOCATION KỸTHUẬT (DEV COLLOCATIONS) - MỚI ---
    # =========================================================
    (r"\bdo a mistake\b", "make a mistake", "Từ dễ nhầm", "Collocation đúng: 'make a mistake' (không phải 'do')"),
    (r"\bdo a decision\b", "make a decision", "Từ dễ nhầm", "Collocation đúng: 'make a decision' (không phải 'do')"),
    (r"\bmake a research\b", "conduct research", "Cụm từ", "Collocation kỹ thuật chuẩn: 'conduct research'"),
    (r"\bdo a analysis\b", "perform an analysis", "Từ dễ nhầm", "Collocation đúng: 'perform an analysis'"),
    (r"\bmake a test\b", "run a test", "Cụm từ", "Collocation kỹ thuật chuẩn: 'run a test'"),
    (r"\bdo a test\b", "run a test", "Cụm từ", "Collocation kỹ thuật chuẩn: 'run a test'"),
    (r"\btake a look on\b", "take a look at", "Giới từ", "Collocation đúng: 'take a look at' (không phải 'on')"),
    (r"\bgive attention on\b", "pay attention to", "Cụm từ", "Collocation đúng: 'pay attention to'"),
    (r"\bdo an effort\b", "make an effort", "Từ dễ nhầm", "Collocation đúng: 'make an effort'"),
    (r"\bfast algorithm\b", "efficient algorithm", "Cụm từ", "Văn phong kỹ thuật chuẩn: 'efficient algorithm'"),
]

# WHITELIST THUẬT NGỮ CÔNG NGHỆ & LẬP TRÌNH (BẢO VỆ 100% KHÔNG BỊ BẮT NHẦM LỖI CHÍNH TẢ)
DEV_TECH_WHITELIST = {
    # Ngôn ngữ & Frameworks
    "fastapi", "asyncio", "pydantic", "sqlite", "postgres", "postgresql", "docker", "k8s",
    "kubernetes", "regex", "json", "yaml", "toml", "agy", "tui", "ui", "cli", "api",
    "jwt", "auth", "repo", "params", "args", "env", "config", "unikey", "evkey",
    "powershell", "cmd", "git", "github", "gitlab", "webhook", "middleware",
    "frontend", "backend", "fullstack", "dev", "prod", "staging", "sdk", "orm",
    "prisma", "redis", "nginx", "graphql", "restful", "grpc", "lint", "venv",
    "virtualenv", "pip", "npm", "yarn", "pnpm", "node", "nodejs", "react", "nextjs",
    "vue", "angular", "svelte", "django", "flask", "fastify", "express", "nestjs",
    "spring", "dotnet", "csharp", "golang", "rust", "typescript", "javascript",
    "python", "kotlin", "swift", "dart", "flutter", "ci", "cd", "devops",
    "ansible", "terraform", "helm", "grafana", "prometheus", "elasticsearch",
    "mongodb", "dynamodb", "kafka", "rabbitmq", "celery", "airflow", "subagent",
    "conpty", "stdout", "stdin", "stderr", "hotkey", "debounce", "refactor",
    "bugfix", "hotfix", "pr", "commit", "push", "pull", "merge", "rebase",
    # Mở rộng whitelist: Cloud, Security, Patterns, Tools
    "dockerfile", "microservices", "serverless", "monorepo", "openapi", "swagger",
    "proto", "protobuf", "websocket", "http2", "oauth", "saml", "ldap", "sso",
    "mfa", "totp", "hmac", "sha256", "md5", "mutex", "semaphore", "goroutine",
    "coroutine", "async", "await", "callback", "monad", "functor", "currying",
    "memoize", "throttle", "eventloop", "polyfill", "transpile", "minify",
    "treeshake", "bundler", "webpack", "vite", "eslint", "prettier", "husky",
    "commitlint", "semver", "changelog", "singleton", "repository", "dependency",
    "injection", "interceptor", "readonly", "nullable", "optional", "generic",
    "interface", "abstract", "runtime", "bytecode", "jit", "aot", "llvm", "wasm",
    "abi", "cron", "daemon", "socket", "tcp", "udp", "ssl", "tls", "dns", "cdn",
    "loadbalancer", "proxy", "gateway", "cluster", "shard", "replica", "healthcheck",
    "liveness", "readiness", "rollback", "canary", "bluegreen", "orm", "dsl",
    "enum", "struct", "trait", "mixin", "decorator", "generator", "iterator",
    "observable", "promise", "deferred", "future", "coroutine", "pipeline",
    "middleware", "plugin", "adapter", "facade", "strategy", "observer",
}

# DANH SÁCH ENDPOINTS CỦA LANGUAGETOOL ĐỂ TỰ ĐỘNG CHUYỂN DỰ PHÒNG (MULTI-ENDPOINT FALLBACK)
LANGUAGETOOL_ENDPOINTS = [
    "https://api.languagetool.org/v2/check",
    "https://languagetool.org/api/v2/check"
]

# GỢI Ý TỪ VỰNG NÂNG CAO (VOCABULARY ENRICHMENT) - TẦNG 3 MỚI
# Chỉ GỢI Ý (không tự động sửa) — giúp người dùng học từ vựng Engineering English cao cấp
DEV_VOCAB_SUGGESTIONS = [
    (r"\buse\b", "utilize / leverage / employ"),
    (r"\bget the result\b", "retrieve the response / fetch the output"),
    (r"\bcheck the error\b", "diagnose the root cause / inspect the exception"),
    (r"\bsend data\b", "transmit payload / dispatch data"),
    (r"\bsave to database\b", "persist to the data store / commit to the database"),
    (r"\bstart the server\b", "initialize the server instance / bootstrap the server"),
    (r"\bstop the server\b", "gracefully shut down the server"),
    (r"\bwrite code\b", "implement / craft the logic / author the routine"),
    (r"\bremove the bug\b", "eliminate the defect / resolve the regression"),
    (r"\bspeed up\b", "optimize / accelerate / improve throughput"),
    (r"\bold code\b", "legacy codebase / deprecated implementation"),
    (r"\brun the test\b", "execute the test suite / trigger CI validation"),
    (r"\bneed to fix\b", "need to resolve / need to patch / need to remediate"),
    (r"\bcheck if\b", "verify whether / validate that / assert that"),
]


def _get_vocab_suggestions(text: str) -> list[str]:
    """
    Tầng 3 Mới: Gợi ý thay thế từ vựng Engineering English cao cấp.
    Chỉ đề xuất, không tự sửa — bảo tồn ý nghĩa gốc của người dùng.
    """
    suggestions = []
    for pattern, suggestion in DEV_VOCAB_SUGGESTIONS:
        matched = re.search(pattern, text, re.IGNORECASE)
        if matched:
            original_word = matched.group(0)
            suggestions.append(f"[Từ vựng] Cân nhắc thay '{original_word}' → {suggestion}")
    return suggestions


def check_and_correct_grammar(text: str) -> Tuple[str, list[str]]:
    """
    Trình kiểm tra và sửa lỗi ngữ pháp tiếng Anh Cấp độ Pro Max ULTRA.
    Xử lý đầy đủ 13 nhóm lỗi + gợi ý từ vựng:
    - [Ngữ pháp]: Chia động từ, số ít/nhiều, danh từ không đếm được, thể bị động.
    - [Thì]: Hiện tại tiếp diễn, quá khứ đơn, hiện tại hoàn thành.
    - [Cú pháp]: Đảo ngữ câu hỏi, mệnh đề quan hệ (who/which/that), câu điều kiện.
    - [Điều kiện]: Type 1/2/3, unless.
    - [Từ dễ nhầm]: Than/then, lose/loose, affect/effect, site/side, past/pass.
    - [Giới từ]: Chuẩn hóa giới từ kỹ thuật (on line, listen on port, depend on...).
    - [Collocation]: make/do/run/conduct + noun chuẩn kỹ thuật.
    - [Chính tả]: Thiếu dấu nháy đơn (don't, can't...), lỗi gõ sai thực sự.
    - [Từ vựng]: Gợi ý nâng cao từ vựng Engineering English (không sửa tự động).
    """
    clean_text = text.strip()
    if not clean_text:
        return clean_text, []

    if clean_text in _GRAMMAR_CACHE:
        return _GRAMMAR_CACHE[clean_text]

    notes = []
    corrected = clean_text

    # ========================================================
    # TẦNG 1: QUY TẮC NGỮ PHÁP DEV TỨC THÌ (LOCAL HEURISTICS - 0ms)
    # ========================================================
    for item in PRO_MAX_GRAMMAR_RULES:
        pattern, replacement, category, reason = item
        if re.search(pattern, corrected, re.IGNORECASE):
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
            # Giữ tương thích với các assert kiểm thử cũ: "Ngữ pháp: <reason>"
            notes.append(f"Ngữ pháp: {reason}" if category == "Ngữ pháp" else f"[{category}] {reason}")

    # ========================================================
    # TẦNG 2: PHÂN TÍCH CHUYÊN SÂU LANGUAGETOOL (MULTI-ENDPOINT NLP)
    # ========================================================
    for endpoint in LANGUAGETOOL_ENDPOINTS:
        try:
            data = urllib.parse.urlencode({
                "text": corrected,
                "language": "en-US"
            }).encode("utf-8")

            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )

            with urllib.request.urlopen(req, timeout=4.5) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
                matches = parsed.get("matches", [])

                # Sắp xếp từ phải qua trái để thay thế không lệch vị trí chuỗi
                matches_sorted = sorted(matches, key=lambda m: m.get("offset", 0), reverse=True)
                for m in matches_sorted:
                    reps = m.get("replacements", [])
                    if reps:
                        best = reps[0].get("value", "")
                        off = m.get("offset", 0)
                        length = m.get("length", 0)
                        old_word = corrected[off:off+length]

                        # Bỏ qua nếu từ thuộc whitelist thuật ngữ lập trình
                        if old_word.lower() in DEV_TECH_WHITELIST:
                            continue

                        cat_id = m.get("rule", {}).get("category", {}).get("id", "").upper()
                        issue_type = m.get("rule", {}).get("issueType", "").lower()
                        msg = m.get("message", "Lỗi ngữ pháp")

                        # Phân loại chuyên sâu các nhóm lỗi
                        if cat_id in ["GRAMMAR", "COLLOCATIONS"] or issue_type in ["grammar", "non-conformance"]:
                            tag = "Ngữ pháp"
                        elif cat_id in ["CONFUSED_WORDS"]:
                            tag = "Từ dễ nhầm"
                        elif cat_id in ["CASING", "CAPITALIZATION"]:
                            tag = "Viết hoa"
                        elif issue_type == "misspelling" or cat_id in ["TYPOS", "MISC"]:
                            tag = "Chính tả"
                        else:
                            tag = "Cú pháp"

                        corrected = corrected[:off] + best + corrected[off+length:]
                        notes.append(f"[{tag}] Sửa: '{old_word}' ➔ '{best}' ({msg})")

            # Endpoint thành công → không gọi fallback
            break
        except Exception:
            # Endpoint lỗi hoặc timeout → thử endpoint tiếp theo
            continue

    # ========================================================
    # TẦNG 3: GỢI Ý TỪ VỰNG NÂNG CAO (VOCABULARY ENRICHMENT - MỚI)
    # ========================================================
    vocab_hints = _get_vocab_suggestions(corrected)
    notes.extend(vocab_hints)

    # Viết hoa chữ cái đầu câu
    if corrected and corrected[0].islower():
        corrected = corrected[0].upper() + corrected[1:]

    # Loại bỏ ghi chú trùng lặp, giữ nguyên thứ tự
    unique_notes = []
    seen = set()
    for n in notes:
        if n not in seen:
            seen.add(n)
            unique_notes.append(n)

    _GRAMMAR_CACHE[clean_text] = (corrected, unique_notes)
    return corrected, unique_notes
