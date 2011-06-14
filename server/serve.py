#!/usr/bin/env python2

import cv
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
        self.sock = None
        self.client = None
        self.phi_list = ['%02d00' % i for i in range(0, 36)]
        self.theta_list = ['0000', '0070', '0139', '0208', '0277', '0347',
                           '0416', '0485', '0554', '0624', '0693', '0762',
                           '0831', '0900']
        self.phi = 0
        self.theta = 0

        # Initialize OpenCV
        cv.NamedWindow("DIP", False)
        cv.ResizeWindow("DIP", 800, 600)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", 9999))
        self.sock.listen(5)

    def connect(self):
        handshake = '\r\n'.join(['HTTP/1.1 101 Web Socket Protocol Handshake',
                                 'Upgrade: WebSocket',
                                 'Connection: Upgrade',
                                 'Sec-WebSocket-Origin: http://localhost:8000',
                                 'Sec-WebSocket-Location: ws://localhost:9999/',
                                 '', '%s'])

        self.client, address = self.sock.accept()
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

    def close(self):
        self.client.close()

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

        if validated:
            self.phi = (self.phi + int(validated[0].split(' ')[0])) % 35
            self.theta = (self.theta + int(validated[0].split(' ')[1])) % 12

    def send(self):
        for v in self.validated:
            print v
            self.client.send('\x00' + v + '\xff')

    def display(self):
        img_name = "%s_%s.png" % (self.phi_list[self.phi],
                                  self.theta_list[self.theta])

        print '(%s, %s) [%s]' % (self.phi_list[self.phi],
                                 self.theta_list[self.theta], img_name)

        img = cv.LoadImage("Images/up/%s" % img_name)
        cv.ShowImage("DIP", img)
        cv.WaitKey(1000)


def main():
    dip = DIPDemo()
    dip.display()
    dip.start()
    while True: # Temporarily
        dip.connect()
        dip.recv()
        dip.display()
        dip.close()


if __name__ == '__main__':
    main()
