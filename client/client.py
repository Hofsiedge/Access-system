# -*- coding:utf-8 -*-

from tkinter import Tk, Frame, Button, Text, Label, StringVar, Entry, END
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from math import log
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from time import sleep
from BinaryProtocol import BinaryProtocol as BP
from random import randint

class App:

    # TODO: rewrite using grid instead of pack
    
    def __init__(self):
        self.tk = Tk()
        self.frame1 = Frame(self.tk, height=200, width=300)
        self.status = StringVar()
        self.input_str = StringVar()
        self.status.set('Loading')
        self.statusBar = Label(self.tk, height=1, relief='sunken', 
                               textvariable=self.status, anchor='w')
        self.passerInfo = StringVar()
        self.passerLabel = Label(self.frame1, height=1, textvariable=self.passerInfo)
        self.input_str.trace("w", lambda name, index, mode, sv=self.input_str: self.read_code(sv))
        self.entry = Entry(self.frame1, textvariable=self.input_str)
        self.button = Button(self.frame1, text='Подключиться к серверу', command=self.connect)

        self.statusBar.pack(side='bottom', fill='x')
        self.entry.pack(side='top')
        self.passerLabel.pack(side='top')
        self.button.pack(side='right')
        self.frame1.pack(side='top', fill='none')
        self.entry.focus_set()

    def read_code(self, sv):
        if len(sv.get()) > 3:
            send_passing(self.sock, int(sv.get()))
            self.passerInfo.set(get_passer_name(self.sock))
            self.entry.delete(0, END)
            
    def connect(self):
        self.sock = FLSocket(2)
        self.sock.connect('localhost', 9091)
        self.button.config(text='Проверить соединение', command=self.test_connection)
        self.status.set('Подключено')
        self.statusBar.config(fg='green')

    def test_connection(self):
        msg = test_connection(self.sock)
        if msg == 'Connection is fine':
            # Change statusBar colour
            self.status.set('Ready to start')
            self.statusBar.config(fg='green')
            self.button.config(text='Закончить день', command=self.disconnect)
        else:
            self.set_error(msg)

    def disconnect(self):
        self.status.set(end_the_day(self.sock))
        self.statusBar.config(fg='blue')

    def set_connecting(self):
        pass

    def set_error(self, msg):
        self.status = msg
        self.statusBar.config(fg='red')

        
def send_passing(sock, user_id):
    sock.send(bytes(divmod(BP.passing(user_id), 256)))

def test_connection(sock):
    sock.send(bytes(divmod(BP.test_connection(), 256)))
    return get_passer_name(sock)

def end_the_day(sock):
    sock.send(bytes(divmod(BP.end_of_the_day(), 256)))
    print(get_passer_name(sock))
    sock.sock.shutdown(SHUT_RDWR)

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
    root = App()


    root.tk.mainloop()

    # try:
    #     test_connection(sock)
    #     while True:
    #         i = int(input())
    #         if not i:
    #             break
    #         send_passing(sock, i)
    #         print(get_passer_name(sock))
    #     end_the_day(sock)
    # except RuntimeError as e:
    #     print(e)
    #     #TODO: indicate in statusbar
    # finally:
    #     sock.close()



