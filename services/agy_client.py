"""
Trình quản lý giao tiếp với Antigravity CLI (AGY Terminal Client)
Hỗ trợ đầy đủ các lệnh hệ thống (/model, /effort, /skills, /agents, /new,...)
và tự động chèn chỉ thị ép buộc phản hồi tiếng Việt cho các prompt thông thường.
"""
import asyncio
import os
import shutil
from typing import AsyncGenerator
from config import AGY_PATH, VIETNAMESE_DIRECTIVE


class AGYClient:
    def __init__(self, agy_executable: str = AGY_PATH):
        self.executable = agy_executable
        self.has_previous_session = False
        self.current_model: str | None = None
        self.current_effort: str | None = None

    def reset_session(self) -> None:
        """
        Bắt đầu phiên làm việc mới (tương đương /new)
        """
        self.has_previous_session = False

    def build_payload(self, prompt: str) -> str:
        """
        Bọc prompt với chỉ thị bắt buộc phản hồi bằng tiếng Việt.
        """
        return f"{VIETNAMESE_DIRECTIVE}\nUser Prompt: {prompt.strip()}"

    async def execute_command(self, cmd_line: str) -> AsyncGenerator[str, None]:
        """
        Thực thi lệnh hoặc prompt thông thường qua AGY CLI.
        """
        trimmed = cmd_line.strip()
        if not trimmed:
            return

        # 1. Xử lý lệnh nội bộ /new
        if trimmed == "/new":
            self.reset_session()
            yield "Đã bắt đầu một phiên làm việc mới (New conversation session started).\n"
            return

        # 2. Xử lý lệnh /model
        if trimmed.startswith("/model"):
            parts = trimmed.split(maxsplit=1)
            if len(parts) == 1:
                # Nếu chỉ gõ /model -> Liệt kê danh sách model có sẵn
                yield "Đang lấy danh sách model từ AGY...\n"
                async for chunk in self._run_raw_cli(["models"]):
                    yield chunk
                if self.current_model:
                    yield f"\n[Model đang kích hoạt: {self.current_model}]\n"
                return
            else:
                # Nếu gõ /model <model_name> -> Thiết lập model
                new_model = parts[1].strip()
                self.current_model = new_model
                yield f"Đã chuyển model sang: {new_model}\n"
                return

        # 3. Xử lý lệnh /effort
        if trimmed.startswith("/effort"):
            parts = trimmed.split(maxsplit=1)
            if len(parts) > 1:
                self.current_effort = parts[1].strip()
                yield f"Đã thiết lập reasoning effort: {self.current_effort}\n"
                return
            else:
                # Gõ /effort không có tham số -> Chạy qua agy để xem hướng dẫn
                async for chunk in self._run_raw_cli(["-p", "/effort"]):
                    yield chunk
                return

        # 4. Các slash command khác (/skills, /agents, /usage, /help,...) -> Chạy trực tiếp qua agy
        if trimmed.startswith("/"):
            args = ["-p", trimmed]
            async for chunk in self._run_raw_cli(args):
                yield chunk
            return

        # 5. Prompt thông thường -> Bọc với chỉ thị tiếng Việt
        full_prompt = self.build_payload(trimmed)
        args = []
        if self.current_model:
            args.extend(["--model", self.current_model])
        if self.current_effort:
            args.extend(["--effort", self.current_effort])
        if self.has_previous_session:
            args.append("-c")
        args.extend(["-p", full_prompt])

        async for chunk in self._run_raw_cli(args):
            yield chunk

        self.has_previous_session = True

    async def _run_raw_cli(self, args: list[str]) -> AsyncGenerator[str, None]:
        full_args = [self.executable] + args

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            process = await asyncio.create_subprocess_exec(
                *full_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode("utf-8", errors="replace")
                yield decoded_line

            await process.wait()

            if process.returncode != 0:
                stderr_data = await process.stderr.read()
                err_text = stderr_data.decode("utf-8", errors="replace").strip()
                if err_text:
                    yield f"\n[Lỗi AGY CLI (Code {process.returncode})]: {err_text}\n"

        except FileNotFoundError:
            yield f"\n[Lỗi]: Không tìm thấy agy tại {self.executable}\n"
        except Exception as exc:
            yield f"\n[Lỗi thực thi]: {str(exc)}\n"
