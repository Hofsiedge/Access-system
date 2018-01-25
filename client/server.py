from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from _thread import start_new_thread
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from BinaryProtocol import BinaryProtocol as BP
import requests

site = 'http://127.0.01:5000'

def send_passer_name(conn, message):
    message = message.encode('utf-8')
    for i in range(len(message)):
        conn.send(bytes(divmod(BP.passing(message[i]), 256)))
    conn.send(bytes(divmod(BP.passing(0), 256)))

def send_command(conn, cmd):
    send_passer_name(conn, requests.post(site + '/command', data={'command': cmd}).text)

def threaded_client(conn):
    try:
        while True:
            data = conn.recv()
            data = data[0] * 256 + data[1]
            data = BP.decode(data)
            print('Received data:', data)
            send_command(conn, data)
    except RuntimeError as e:
        print(e)
    #except Exception as e:
        #print('Exception caught')
        #print(e)
    finally:
        conn.close()

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 9091))
    sock.listen(3)

    while True:
        conn, addr = sock.accept()
        conn = FLSocket(2, conn)
        print('Connected: ', addr)

        start_new_thread(threaded_client, (conn,))
