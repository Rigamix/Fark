"""Fark dev server: static files, plus one endpoint that lets prop_lab.html
save straight over assets/prop_templates.js.

`python -m http.server` cannot take a POST, so the lab could only ever offer a
download that had to be copied into place by hand. This is that server with a
single extra route:

    POST /__save/prop_templates   ->  writes assets/prop_templates.js

That is the ONLY path it will write. The name is not taken from the request,
so nothing a page sends can make it write anywhere else.

    python tools/dev_server.py [port] [--root DIR]

Defaults to port 8083 and the repo root. CORS is open because the lab is
usually opened straight off disk, where the page's origin is "null".
"""
import sys, os, json, posixpath
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the one file a page is allowed to overwrite, relative to ROOT
SAVE_TARGETS = {
    "prop_templates": os.path.join("assets", "prop_templates.js"),
}
MAX_BYTES = 1 << 20   # a template file is a couple of KB; this is generous


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def end_headers(self):
        self._cors()
        # the dev cache hiding a freshly saved file is a whole class of
        # phantom bug - never let it happen here
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        path = posixpath.normpath(self.path.split("?", 1)[0])
        if not path.startswith("/__save/"):
            self.send_error(404, "no such endpoint")
            return
        key = path[len("/__save/"):]
        target = SAVE_TARGETS.get(key)
        if not target:
            self.send_error(404, "unknown save target %r" % key)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0 or n > MAX_BYTES:
            self.send_error(413, "body must be 1..%d bytes" % MAX_BYTES)
            return
        body = self.rfile.read(n).decode("utf-8", "replace")
        full = os.path.join(ROOT, target)
        # write beside the target and replace, so a half-written file can
        # never be what the game loads next
        tmp = full + ".tmp"
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        os.replace(tmp, full)
        out = json.dumps({"ok": True, "path": target, "bytes": len(body)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)
        sys.stderr.write("saved %s (%d bytes)\n" % (target, len(body)))



def main():
    port, argv = 8083, sys.argv[1:]
    if "--root" in argv:
        i = argv.index("--root")
        globals()["ROOT"] = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    if argv:
        port = int(argv[0])
    # A SECOND LISTENER ON THE SAME PORT IS THE FAILURE, NOT THE SYMPTOM.
    # Three of these were found stacked on 8084, and two probe runs came back
    # as error pages because connections landed on a wedged one.
    # ThreadingHTTPServer sets allow_reuse_address = 1, and on Windows
    # SO_REUSEADDR behaves like SO_REUSEPORT - so a second bind to a LIVE port
    # succeeds instead of failing, and every re-launch quietly added to the pile.
    # Nothing is killed here: a server that reaps processes it did not start is
    # a worse failure than the one being fixed. Refusing loudly is the limit.
    import socket as _sock
    _probe = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
    _probe.settimeout(0.6)
    _busy = (_probe.connect_ex(("127.0.0.1", port)) == 0)
    _probe.close()
    if _busy:
        print("REFUSING TO START: something already listens on %d." % port)
        print("  Starting anyway would ADD a listener, not replace it, and")
        print("  connections would be split between them - which is how two")
        print("  probe runs came back as error pages.")
        print("  Clear it first:  netstat -ano | grep :%d" % port)
        print("                   taskkill //PID <pid> //F")
        sys.exit(1)
    ThreadingHTTPServer.allow_reuse_address = False
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as e:
        print("REFUSING TO START: port %d is not free (%s)" % (port, e))
        sys.exit(1)
    print("fark dev server on http://localhost:%d  (root %s)" % (port, ROOT))
    print("  prop_lab save endpoint: POST /__save/prop_templates")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
