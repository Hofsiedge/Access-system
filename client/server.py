from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from _thread import start_new_thread
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket


def threaded_client(conn):
    try:
        while True:
            data = bytes(HMCode.get_data(i) for i in conn.recv())
            print('Data: ', list(data))
            conn.send(bytes([HMCode.get_code(i) for i in data]))
    except RuntimeError as e:
        print(e)
    finally:
        conn.close()

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 9092))
    sock.listen(3)

    HMCode = HammingCodec(16)

    while True:
        conn, addr = sock.accept()
        conn.settimeout(10)
        conn = FLSocket(3, conn)
        print('Connected: ', addr)

        start_new_thread(threaded_client, (conn,))
