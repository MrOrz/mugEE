#!/usr/bin/env python2

import BaseHTTPServer
import SimpleHTTPServer

from os import chdir, spawnv, kill, P_NOWAIT
from os.path import join
from signal import CTRL_BREAK_EVENT

PORT = 8000

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    pass


def start_server():
    """Start the server."""

    chdir(join('..', 'view'))
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Server stopped.'

def start_websocket_server():
    """Start the websocket server."""
    chdir('server')
    spawnv(P_NOWAIT, "C:\\Python27\\python.exe",
           ["python.exe", "serve.py"])


if __name__ == "__main__":
    start_websocket_server()
    start_server()
