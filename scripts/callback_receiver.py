from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json

OUTPUT = Path("screenshots/kaggle_urls.json")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        payload = json.loads(body.decode("utf-8"))
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, _format, *args):
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8765), Handler).serve_forever()
