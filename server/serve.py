#!/usr/bin/env python2

import cv
import os
import re
import socket
import sys
import threading
import time

from struct import pack
from hashlib import md5

alive = True

def clamp(v, l, h):
    return l if v < l else (h if v > h else v)

class ConnectionFailed(Exception):
    pass

class ConnectionNotEstablished(Exception):
    pass

class DIPDemo(object):
    def __init__(self):
        self.sock = None
        self.client = None
        self.phi_list = ['%02d00' % i for i in range(0, 36)]
        self.theta_list = ['0900', '0831', '0762', '0693', '0624', '0554',
                           '0485', '0416', '0347', '0277', '0208', '0139',
                           '0070', '0000',
                           '0000', '0070', '0139', '0208', '0277', '0347',
                           '0416', '0485', '0554', '0624', '0693', '0762',
                           '0831', '0900']

        self.phi = 0
        self.theta = 14
        self.pole = 'p'

        self.img = None
        self.mask = None
        self.hsv = cv.CreateImage((1167, 1024), cv.IPL_DEPTH_8U, 3)
        self.hue = cv.CreateImage((1167, 1024), cv.IPL_DEPTH_8U, 1)
        self.sat = cv.CreateImage((1167, 1024), cv.IPL_DEPTH_8U, 1)
        self.val = cv.CreateImage((1167, 1024), cv.IPL_DEPTH_8U, 1)
        self.final = cv.CreateImage((1167, 1024), cv.IPL_DEPTH_8U, 3)
        self.op = 'CHI'

        #: Initialize OpenCV
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

        for v in validated:
            v = v.split(' ')
            if v[0] == 'offset':
                self.phi = clamp(self.phi + int(v[1]), 0, 35)
                self.theta = clamp(self.theta + int(v[2]), 0, 27)

                self.op = 'CHI'
            elif v[0] == 'abs':
                self.phi = int(self.phi_list.index(v[1]))
                self.theta = 27 - int(self.theta_list.index(v[2]))
                self.op = 'CHI'
            elif v[0] == 'hsl':
                self.op = 'HSI'

            self.pole = 'p' if self.theta >= 14 else 'n'

    def send(self):
        for v in self.validated:
            print v
            self.client.send('\x00' + v + '\xff')

    def display(self):
        if self.op == 'CHI':
            img_name = "%s_%s_%s" % (self.pole, self.theta_list[self.theta],
                                     self.phi_list[self.phi])

            print '(%s, %s) [%s]' % (self.theta_list[self.theta],
                                     self.phi_list[self.phi], img_name)

            self.img = cv.LoadImage("Images/%s.png" % img_name, 1)
            self.mask = cv.LoadImage("Images/%s-mask.png" % img_name, 0)
            cv.CvtColor(self.img, self.hsv, cv.CV_BGR2HSV)
            cv.Split(self.hsv, self.hue, self.sat, self.val, None)
        elif self.op == 'HSI':
            cv.AddS(self.val, 10, self.val)
            cv.Merge(self.hue, self.sat, self.val, None, self.hsv)
            cv.CvtColor(self.hsv, self.img, cv.CV_HSV2RGB)

        cv.Set(self.final, 0)
        cv.Copy(self.img, self.final, self.mask)
        cv.ShowImage("DIP", self.final)
        cv.WaitKey(1000)

    def _parse_header(self, header):
        self.header_dict = { i[0]: i[1] for i in
                        [ i.split(': ') for i in header.split('\r\n')[1:-2] ] } 

    def _get_key_value(self, key):
        key_value = self.header_dict[key]
        key_number = int(re.sub("\\D", "", key_value))
        spaces = re.subn(" ", "", key_value)[1]
        part = key_number / spaces
        return part


def UpdateGUI():
    """Execute OpenCV's HighGUI event loop, prevent window from not responding.
    """
    while alive:
        cv.WaitKey(1000)
        time.sleep(1)


def onExit(*args):
    global alive
    alive = False
    sys.exit(0)


def main():
    #: Register exit function
    if os.name == 'posix':
        import signal
        signal.signal(signal.SIGTERM, onExit)
    else:
        import win32api
        win32api.setConsoleCtrlHandler(onExit, True)

    #: Start DIPDemo
    dip = DIPDemo()
    dip.display()
    dip.start()

    #: Start background thread
    thread = threading.Thread(target=UpdateGUI)
    thread.start()

    while True:
        dip.connect()
        while True:
            dip.recv()
            dip.display()
        dip.close()

if __name__ == '__main__':
    main()
