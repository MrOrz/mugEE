#!/usr/bin/env python2

import BaseHTTPServer
import SimpleHTTPServer

from os import chdir, fork, execv

PORT = 8000

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    pass


def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Server stopped.'

def start_websocket_server():
    """Start the websocket server."""
    pid = fork()
    if pid == 0:
        execv("./serve.py", ["./serve.py"])

if __name__ == "__main__":
    chdir('server')
    start_websocket_server()
    start_server()
