# -*- coding:utf-8 -*-

from tkinter import Tk, Frame, Button, Text, Label, StringVar
from socket import socket, AF_INET, SOCK_STREAM
from math import log
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from time import sleep
from BinaryProtocol import BinaryProtocol as BP
from random import randint

class App:
    
    def __init__(self):
        self.tk = Tk()
        self.frame1 = Frame(self.tk, height=200, width = 300)
        self.status = StringVar()
        self.status.set('Loading')
        self.statusBar = Label(self.tk, height=1, relief='sunken', 
                               textvariable=self.status, anchor='w')

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

        
def send_passing(sock, user_id):
    sock.send(bytes(divmod(BP.passing(user_id), 256)))

def test_connection(sock):
    sock.send(bytes(divmod(BP.test_connection(), 256)))

def end_the_day(sock):
    sock.send(bytes(divmod(BP.end_of_the_day(), 256)))

def get_passer_name(sock):
    #TODO: more efficient way to do this
    cur_char = 1
    data = []
    while cur_char:
        data.append(cur_char)
        cur_char = sock.recv()
        cur_char = BP.decode(cur_char[0] * 256 + cur_char[1])
    return bytes(data[1:]).decode('utf-8')


if __name__ == '__main__':
    #root = App()
    #root.tk.mainloop()

    sock = FLSocket(2)
    sock.connect('localhost', 9090)
    try:
        while True:
            i = randint(0, 8)
            sleep(1)
            send_passing(sock, i)
            print(get_passer_name(sock))
            #data = sock.recv()
            #data = BP.decode(data[0] * 256 + data[1])
            #print('Data: ', data)
    except RuntimeError as e:
        print(e)
        #TODO: indicate in statusbar
    finally:
        sock.close()

