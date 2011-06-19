#!/usr/bin/env python2

import BaseHTTPServer
import SimpleHTTPServer
import os
import os.path

PORT = 8000

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    pass


def start_server():
    """Start the server."""
    os.chdir(os.path.join('..', 'view'))
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Server stopped.'

def start_websocket_server():
    """Start the websocket server."""
    os.chdir('server')
    if os.name == 'posix':
        os.spawnvp(os.P_NOWAIT, "python2", ["python2", "serve.py"])
    else:
        os.spawnv(os.P_NOWAIT, "C:\\Python27\\python.exe",
                  ["python.exe", "serve.py"])


if __name__ == "__main__":
    start_websocket_server()
    start_server()
