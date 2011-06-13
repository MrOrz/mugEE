#!/usr/bin/env python2

import re
import socket
import sys

from struct import pack
from hashlib import md5

class ConnectionFailed(Exception):
    pass

class ConnectionNotEstablished(Exception):
    pass

class DIPDemo(object):
    def __init__(self):
        self.client = None

    def connect(self):
        handshake = '\r\n'.join(['HTTP/1.1 101 Web Socket Protocol Handshake',
                                 'Upgrade: WebSocket',
                                 'Connection: Upgrade',
                                 'Sec-WebSocket-Origin: http://localhost:8000',
                                 'Sec-WebSocket-Location: ws://localhost:9999/',
                                 '', '%s'])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 9999))
        sock.listen(5)

        self.client, address = sock.accept()
        header = self.client.recv(4096)
        if header.find('\r\n\r\n') != -1:
            self._parse_header(header)
            header = header.split('\r\n')

            key1 = self._get_key_value('Sec-WebSocket-Key1')
            key2 = self._get_key_value('Sec-WebSocket-Key2')

            challenge = ''
            challenge += pack('!I', key1)
            challenge += pack('!I', key2)
            challenge += header[-1]
            challenge = md5(challenge).digest()
            self.client.send(handshake % challenge)
        else:
            raise ConnectionFailed

    def _parse_header(self, header):
        self.header_dict = { i[0]: i[1] for i in
                        [ i.split(': ') for i in header.split('\r\n')[1:-2] ] } 

    def _get_key_value(self, key):
        key_value = self.header_dict[key]
        key_number = int(re.sub("\\D", "", key_value))
        spaces = re.subn(" ", "", key_value)[1]
        part = key_number / spaces
        return part
    
    def recv(self):
        if not self.client:
            raise ConnectionNotEstablished

        data = self.client.recv(4096)

        validated = []

        msgs = data.split('\xff')
        data = msgs.pop()

        for msg in msgs:
            if msg[0] == '\x00':
                validated.append(msg[1:])

        self.validated = validated

    def send(self):
        for v in self.validated:
            print v
            self.client.send('\x00' + v + '\xff')


def main():
    dip = DIPDemo()
    dip.connect()
    dip.recv()
    dip.send()


if __name__ == '__main__':
    main()
