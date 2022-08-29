import argparse
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

parser = argparse.ArgumentParser()

parser.add_argument("--host", help="The hostname of the server, e.g. localhost", default="localhost")
parser.add_argument("--port", help="The port used to run the server, e.g. 8000", default="8000")

args = parser.parse_args()


class DPServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        super().__init__(*args, **kwargs, directory=dir_path, **kwargs)

    def end_headers(self):
        if self.path.startswith("/static") and not self.path.endswith(".js"):
            self.send_header("Content-Encoding", "gzip")
        super().end_headers()


def main():
    server = HTTPServer((args.host, int(args.port)), DPServer)
    print(f"Server started at {args.host}:{args.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped")


main()
