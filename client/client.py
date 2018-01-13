# -*- coding:utf-8 -*-

from tkinter import Tk, Frame, Button, Text, Label, StringVar
from socket import socket, AF_INET, SOCK_STREAM
from math import log
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from time import sleep

class App:
    
    def __init__(self):
        self.tk = Tk()
        self.frame1 = Frame(self.tk, height=200, width = 300)
        self.status = StringVar()
        self.status.set('Loading')
        self.statusBar = Label(self.tk, height=1, relief='sunken', textvariable=self.status, anchor='w')

        self.frame1.pack(side='top')
        self.statusBar.pack(side='bottom', fill='x')

    def connect():
        pass

    def set_ready(self):
        pass

    def set_connecting(self):
        pass

    def set_error(self):
        pass

        
if __name__ == '__main__':
    #root = App()
    #root.tk.mainloop()

    HMCode = HammingCodec(16)

    sock = FLSocket(3)
    sock.connect('localhost', 9092)
    try:
        while True:
            sleep(1)
            sock.send(bytes([HMCode.get_code(i) for i in [15, 15, 15]]))
            data = sock.recv()
            data = bytes([HMCode.get_data(i) for i in data])
            print('Data: ', list(data))
    except RuntimeError as e:
        print(e)
    finally:
        sock.sock.close()

