# -*- coding: utf-8 -*-
"""
H5 轻应用交互 · 本地服务端
=========================================
职责：
  1. 托管 static/ 下的 H5 静态页面（问卷 + 两个趣味测试）
  2. 提供 /api/records 接口，读写 data/records.json

技术路线：Python 标准库 http.server，不依赖任何第三方包。
这样在 PyCharm 里新建/打开项目后，点运行即可启动，无需 pip install。

运行方式：
  PyCharm 中右键 app.py → Run 'app'
  或命令行：python app.py
  浏览器访问：http://127.0.0.1:8000
"""

import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_FILE = os.path.join(BASE_DIR, "data", "records.json")
PORT = int(os.environ.get("PORT", 8000))

_lock = threading.Lock()


def load_records():
    """读取全部记录，文件不存在或损坏时返回空列表。"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_records(records):
    """写回记录文件，最多保留最近 200 条。"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as fp:
        json.dump(records[:200], fp, ensure_ascii=False, indent=2)


class Handler(SimpleHTTPRequestHandler):
    """静态托管 + 记录接口。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    # ---------- 统一 JSON 输出 ----------
    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    # ---------- GET ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/records":
            client = (parse_qs(parsed.query).get("client") or [""])[0]
            with _lock:
                records = load_records()
            if client:
                records = [r for r in records if r.get("client") == client]
            records.sort(key=lambda r: r.get("time", 0), reverse=True)
            self._json({"ok": True, "records": records})
            return
        super().do_GET()

    # ---------- POST ----------
    def do_POST(self):
        if urlparse(self.path).path != "/api/records":
            self._json({"ok": False, "error": "not found"}, 404)
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            record = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json({"ok": False, "error": "invalid json"}, 400)
            return

        if not isinstance(record, dict) or "job" not in record:
            self._json({"ok": False, "error": "invalid record"}, 400)
            return

        with _lock:
            records = load_records()
            records.insert(0, record)
            save_records(records)

        self._json({"ok": True, "count": len(records)})

    # ---------- 日志精简 ----------
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("=" * 52)
    print(" H5 轻应用交互 本地服务已启动")
    print(" 问卷首页  http://127.0.0.1:%d/" % PORT)
    print(" 五行命格  http://127.0.0.1:%d/wuxing/" % PORT)
    print(" 色彩人格  http://127.0.0.1:%d/color/" % PORT)
    print(" 记录接口  http://127.0.0.1:%d/api/records" % PORT)
    print("=" * 52)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
