#! venv/bin/python3.5
# -*- coding:utf-8 -*-

from tkinter import Tk, Frame, StringVar, Label, PhotoImage, Entry, Button, END, W, E, N, S
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from time import sleep
from random import randint
from base64 import b64encode
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from BinaryProtocol import BinaryProtocol as BP

class App:

    def __init__(self):
        self.tk = Tk()
        self.frame1 = Frame(self.tk)
        self.frame2 = Frame(self.tk)
        self.status = StringVar()
        self.input_str = StringVar()
        self.input_str.trace("w", lambda name, index, mode, sv=self.input_str: self.read_code(sv))
        self.status.set('Загрузка')
        self.statusBar = Label(self.tk, height=1, relief='sunken', textvariable=self.status, anchor='w')
        self.passerSurname = StringVar()
        self.passerName = StringVar()
        self.passerPatronymic = StringVar()
        # instead of receiving an image
        with open('../image_min.gif', 'rb') as f:
            self.passerPhoto = b64encode(f.read())
            # It seems to work properly this way, but not sure
            # self.passerPhoto = f.read()
        self.photo = PhotoImage(data=self.passerPhoto, format='gif')
        self.photo_label = Label(self.frame2, image=self.photo)
        self.surname_label = Label(self.frame2, height=1, width=30, textvariable=self.passerSurname, anchor='w', bg='yellow')
        self.name_label = Label(self.frame2, height=1, width=30, textvariable=self.passerName, anchor='w', bg='yellow')
        self.patronymic_label = Label(self.frame2, height=1, width=30, textvariable=self.passerPatronymic, anchor='w', bg='green')

        self.entry = Entry(self.frame1, textvariable=self.input_str)
        self.button = Button(self.frame1, text='Подключиться к серверу', command=self.connect)

        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.frame2.grid(row=0, column=1, sticky=E)
        self.statusBar.grid(row=1, columnspan=3, sticky=W+E)

        self.entry.grid(row=0, column=0)
        self.button.grid(row=1, rowspan=2, column=0)

        self.surname_label.grid(row=0, column=1, sticky=E)
        self.name_label.grid(row=1, column=1, sticky=E)
        self.patronymic_label.grid(row=2, column=1, sticky=E)
        self.photo_label.grid(row=0, column=0, rowspan=3, sticky=E)

        self.tk.resizable(False, False)
        self.entry.focus_set()
        self.entry.grab_set()

    def read_code(self, sv):
        if len(sv.get()) > 3:
            send_passing(self.sock, int(sv.get()))
            passerInfo = get_passer_name(self.sock).split(maxsplit=3)
            self.entry.delete(0, END)
            self.passerSurname.set(passerInfo[0])
            self.passerName.set(passerInfo[1])
            self.passerPatronymic.set(passerInfo[2])
            self.photo = passerInfo[3]
            # TODO: check
            # is this necessary?
            # self.photo_label.config(image=self.photo)
            
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



