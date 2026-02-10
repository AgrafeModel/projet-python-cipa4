import threading
import time
import webbrowser
import requests
import os
import shutil

# Re gexes for parsing ollama output
import re
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
PCT_RE = re.compile(r"(\d{1,3})%")
SIZE_RE = re.compile(r"(\d+(\.\d+)?)\s*GB\s*/\s*(\d+(\.\d+)?)\s*GB")

# Ollama-related utilities: checking status, pulling models, etc.
OLLAMA_URL = "http://localhost:11434"
OLLAMA_DOWNLOAD_PAGE = "https://ollama.ai/download"
DEFAULT_MODEL = "mistral"

# Ollama utilities: checking status, pulling models, etc.
def open_ollama_download():
    webbrowser.open(OLLAMA_DOWNLOAD_PAGE)

# Ollama API utilities
def get_tags(timeout: float = 0.15):
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

# Checks if Ollama is running by trying to fetch tags (with a short timeout)
def is_ollama_running(timeout: float = 0.15) -> bool:
    return get_tags(timeout=timeout) is not None

# Checks if a specific model is available in Ollama by fetching tags and looking for the model name
def has_model(model_name: str = DEFAULT_MODEL, timeout: float = 0.15) -> bool:
    data = get_tags(timeout=timeout)
    if not data:
        return False

    model_name = model_name.lower()
    models = data.get("models", [])
    for m in models:
        name = (m.get("name") or "").lower()
        # "mistral:latest" : "mistral"
        if model_name in name:
            return True
    return False

# Finds the Ollama executable by checking PATH and common installation directories
def find_ollama_exe() -> str | None:
    # PATH
    p = shutil.which("ollama")
    if p:
        return p

    # Common installation paths
    candidates = []

    # Program Files
    candidates.append(r"C:\Program Files\Ollama\ollama.exe")
    candidates.append(r"C:\Program Files (x86)\Ollama\ollama.exe")

    # LocalAppData
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(os.path.join(local, "Programs", "Ollama", "ollama.exe"))
        candidates.append(os.path.join(local, "Ollama", "ollama.exe"))

    for c in candidates:
        if os.path.exists(c):
            return c

    return None

# Pulls a model from Ollama in a background thread, providing callbacks for progress, status updates, completion, and errors
def pull_model_async(model_name: str, on_done=None, on_error=None, on_progress=None, on_status=None):
    import subprocess, threading, os, time

    def worker():
        try:
            exe = find_ollama_exe()
            if not exe:
                msg = "Ollama introuvable (PATH)."
                print(f"[OLLAMA] ERROR: {msg}")
                if on_error: on_error(msg)
                return

            print(f"[OLLAMA] Starting: {exe} pull {model_name}")

            # Start the pull process and read output in real-time to provide feedback
            p = subprocess.Popen(
                [exe, "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )

            buffer = ""
            last_percent = -1

            # Function to handle text output from the pull process, parsing status lines and progress updates
            def handle_text(txt: str):
                nonlocal last_percent, buffer
                # remove ANSI
                clean = ANSI_RE.sub("", txt)
                buffer += clean

                # split on newlines OR on carriage return-like updates
                parts = re.split(r"[\r\n]+", buffer)
                buffer = parts[-1]  # keep tail (incomplete)
                lines = parts[:-1]

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    print(f"[OLLAMA] {line}")

                    # status updates
                    if on_status:
                        on_status(line)

                    # percent
                    m = PCT_RE.search(line)
                    if m:
                        pct = int(m.group(1))
                        pct = max(0, min(100, pct))
                        if pct != last_percent:
                            last_percent = pct
                            if on_progress:
                                on_progress(pct)

            # Read output in real-time and handle it
            if p.stdout:
                while True:
                    chunk = p.stdout.read(256)
                    if chunk:
                        txt = chunk.decode("utf-8", errors="replace")
                        handle_text(txt)
                    else:
                        if p.poll() is not None:
                            break
                        time.sleep(0.05)

            rc = p.wait()
            if rc == 0:
                print("[OLLAMA] Pull finished successfully.")
                if on_progress:
                    on_progress(100)
                if on_done:
                    on_done()
            else:
                msg = f"ollama pull exited with code {rc}"
                print(f"[OLLAMA] ERROR: {msg}")
                if on_error:
                    on_error(msg)

        except Exception as e:
            print(f"[OLLAMA] EXCEPTION: {e}")
            if on_error:
                on_error(str(e))

    # Start the worker thread to pull the model without blocking the main application
    threading.Thread(target=worker, daemon=True).start()

# Removes a model from Ollama in a background thread, used for cleanup if the user quits during a download to avoid leaving a broken state
def rm_model_async(model: str):
    # Import here to avoid circular imports if we call this from the screens.py cleanup while we're still importing the ollama installer for the pull_model_async function
    import subprocess

    def worker():
        ollama_path = shutil.which("ollama") or "ollama"
        cmd = [ollama_path, "rm", model]
        print(f"[OLLAMA] Cleanup: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[OLLAMA] Cleanup exception: {e}")

    threading.Thread(target=worker, daemon=True).start()
