#!/usr/bin/env python3

from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


PORT = 8000
print(f"Server starting on port {PORT}")
httpd = HTTPServer(("localhost", PORT), CORSRequestHandler)
httpd.serve_forever()
