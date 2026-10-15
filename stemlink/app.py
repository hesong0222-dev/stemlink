"""stemlink: 유튜브 링크 → 보컬/드럼/베이스/나머지 분리. 내 맥에서만 도는 작은 웹 앱."""
import json, os, re, subprocess, sys, threading, uuid, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("STEMLINK_PORT", "7860"))
OUT = Path(os.environ.get("STEMLINK_DIR", Path.home() / "Music" / "stemlink"))
PAGE = (Path(__file__).parent / "index.html").read_bytes()
jobs = {}


def device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    return "cuda" if torch.cuda.is_available() else "cpu"


def run(job_id, url):
    job = jobs[job_id]
    work = OUT / job_id
    work.mkdir(parents=True, exist_ok=True)
    try:
        job["step"] = "소리 받는 중"
        got = subprocess.run([sys.executable, "-m", "yt_dlp", "-f", "bestaudio", "-x", "--audio-format", "wav", "--no-playlist",
                              "-o", str(work / "source.%(ext)s"), "--print", "after_move:title", url],
                             check=True, capture_output=True, text=True)
        title = got.stdout.strip()
        job["title"] = title or url
        job["step"] = "악기별로 나누는 중 (곡 길이만큼 걸려요)"
        subprocess.run([sys.executable, "-m", "demucs", "-n", "htdemucs", "-d", device(), "--mp3",
                        "-o", str(work), str(work / "source.wav")], check=True, capture_output=True, text=True)
        stems = work / "htdemucs" / "source"
        job["stems"] = {p.stem: f"/files/{job_id}/htdemucs/source/{p.name}" for p in sorted(stems.glob("*.mp3"))}
        job["step"] = "완료"
    except subprocess.CalledProcessError as e:
        job["step"] = "실패"
        job["error"] = (e.stderr or str(e))[-500:]


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE)
        elif self.path.startswith("/api/job/"):
            self.send_json(jobs.get(self.path.rsplit("/", 1)[-1], {"step": "없음"}))
        elif self.path.startswith("/files/") and ".." not in self.path:
            self.path = self.path[len("/files"):]
            super().do_GET()
        else:
            self.send_error(404)

    def translate_path(self, path):
        return str(OUT / path.lstrip("/"))

    def do_POST(self):
        if self.path != "/api/split":
            return self.send_error(404)
        url = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["url"].strip()
        if not re.match(r"^https?://(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/", url):
            return self.send_json({"error": "유튜브 링크만 돼요"}, 400)
        job_id = uuid.uuid4().hex[:8]
        jobs[job_id] = {"step": "대기", "url": url}
        threading.Thread(target=run, args=(job_id, url), daemon=True).start()
        self.send_json({"id": job_id})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"stemlink: http://127.0.0.1:{PORT}  (결과 저장: {OUT})")
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
