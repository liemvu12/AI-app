"""
Module theo dõi nhật ký AGY thời gian thực (Real-time AGY Transcript Watcher)
Tự động phát hiện prompt người dùng vừa nhập vào terminal gốc AGY và kích hoạt phân tích tiếng Anh.
"""
import os
import glob
import json
import re
import time
import threading
from typing import Callable

BRAIN_DIR = os.path.expanduser(r"~/.gemini/antigravity-cli/brain")


class AGYTranscriptWatcher:
    def __init__(self, on_new_prompt: Callable[[str], None], poll_interval: float = 0.2):
        self.on_new_prompt = on_new_prompt
        self.poll_interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._current_file: str | None = None
        self._last_file_size: int = 0
        self._seen_prompts: set[str] = set()

    def get_latest_transcript_file(self) -> str | None:
        """
        Tìm file transcript.jsonl của phiên hội thoại mới nhất
        """
        if not os.path.isdir(BRAIN_DIR):
            return None

        t_files = glob.glob(os.path.join(BRAIN_DIR, "*", ".system_generated", "logs", "transcript.jsonl"))
        if not t_files:
            return None

        # Sắp xếp trực tiếp theo thời gian sửa đổi của chính file transcript.jsonl
        t_files.sort(key=os.path.getmtime, reverse=True)
        return t_files[0]

    def start(self) -> None:
        if self._running:
            return
        self._running = True

        # Khởi tạo vị trí đọc từ cuối file để chỉ bắt các prompt mới
        latest = self.get_latest_transcript_file()
        if latest and os.path.exists(latest):
            self._current_file = latest
            self._last_file_size = os.path.getsize(latest)

        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _watch_loop(self) -> None:
        while self._running:
            try:
                latest = self.get_latest_transcript_file()
                if not latest or not os.path.exists(latest):
                    time.sleep(self.poll_interval)
                    continue

                # Nếu phiên hội thoại chuyển sang file mới (hoặc mới mở)
                if latest != self._current_file:
                    self._current_file = latest
                    self._last_file_size = 0

                current_size = os.path.getsize(latest)
                if current_size > self._last_file_size:
                    # Đọc phần nội dung mới thêm vào
                    with open(latest, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(self._last_file_size)
                        new_lines = f.readlines()
                        self._last_file_size = f.tell()

                    for line in new_lines:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if data.get("type") == "USER_INPUT":
                                raw = data.get("content", "")
                                match = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", raw, re.DOTALL)
                                prompt_text = match.group(1).strip() if match else raw.strip()
                                
                                if prompt_text and prompt_text not in self._seen_prompts:
                                    self._seen_prompts.add(prompt_text)
                                    self.on_new_prompt(prompt_text)
                        except Exception:
                            pass
            except Exception:
                pass

            time.sleep(self.poll_interval)
