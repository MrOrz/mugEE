#!/usr/bin/env python2

import BaseHTTPServer
import SimpleHTTPServer

from os import chdir, fork, execv, kill
from signal import SIGTERM

PORT = 8000
CPID = 0

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    pass


def start_server():
    """Start the server."""
    global CPID
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        kill(CPID, SIGTERM)
        print 'Server stopped.'

def start_websocket_server():
    """Start the websocket server."""
    global CPID

    pid = fork()
    if pid == 0:
        execv("./serve.py", ["./serve.py"])
    else:
        CPID = pid


if __name__ == "__main__":
    chdir('server')
    start_websocket_server()
    start_server()
