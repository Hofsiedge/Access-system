# -*- coding:utf-8 -*-

from tkinter import Tk, Frame, Button, Text, Label, StringVar
from socket import socket, AF_INET, SOCK_STREAM

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

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('localhost', 9092))
    #sock.send('hello, world!'.encode('utf-8'))
    sock.send(input().encode('utf-8'))
    sock.shutdown(1)

    data = ''

    #data = sock.recv(4096).decode('utf-8')
    while True:
        tmp_data = sock.recv(1024)
        print('Temporary: ' + tmp_data.decode('utf-8'))
        data += tmp_data.decode('utf-8')
        if not tmp_data:
            sock.close()
            break

    print('Data: ' + data)

    #print(data.decode('utf-8'))

    sock.close()

