import urllib.request
import urllib.parse
import json
import os
import subprocess
import tempfile
import threading
from typing import Callable, Optional

OLLAMA_API_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"

def is_ollama_running() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_API_URL}/")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False

def generate_text(prompt: str, system_prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not is_ollama_running():
        raise Exception("Ollama is not running")
        
    url = f"{OLLAMA_API_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "keep_alive": "30m"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req, timeout=30.0) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()

def download_file(url: str, dest: str, progress_callback: Callable[[int, int], None]) -> None:
    req = urllib.request.urlopen(url)
    total_size = int(req.info().get("Content-Length", 0))
    downloaded = 0
    chunk_size = 8192
    
    with open(dest, "wb") as f:
        while True:
            chunk = req.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if progress_callback and total_size > 0:
                progress_callback(downloaded, total_size)

def install_ollama_silently(progress_callback: Callable[[int, int], None], status_callback: Callable[[str], None]) -> bool:
    installer_url = "https://ollama.com/download/OllamaSetup.exe"
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "OllamaSetup.exe")
    
    try:
        status_callback("Đang tải bộ cài Ollama (dung lượng ~100MB)...")
        download_file(installer_url, installer_path, progress_callback)
        
        status_callback("Đang tiến hành cài đặt ngầm...")
        # Setup im lặng, không hiện UI
        subprocess.run([installer_path, "/SILENT"], check=True)
        return True
    except Exception as e:
        status_callback(f"Lỗi cài đặt: {e}")
        return False

def pull_model_with_progress(model: str, progress_callback: Callable[[int, int, str], None]) -> bool:
    url = f"{OLLAMA_API_URL}/api/pull"
    payload = {"name": model, "stream": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    status = chunk.get("status", "")
                    total = chunk.get("total", 0)
                    completed = chunk.get("completed", 0)
                    if progress_callback:
                        progress_callback(completed, total, status)
        return True
    except Exception as e:
        return False
