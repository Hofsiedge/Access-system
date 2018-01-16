from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from _thread import start_new_thread
from HammingCode import HammingCodec
from SocketFixedLen import FLSocket
from BinaryProtocol import BinaryProtocol as BP

pseudo_database = {0: 'Фамилия1 Имя1 Отчество1',
                   1: 'Фамилия2 Имя2 Отчество2',
                   2: 'Фамилия3 Имя3 Отчество3',
                   3: 'Фамилия4 Имя4 Отчество4',
                   4: 'Фамилия5 Имя5 Отчество5',
                   5: 'Фамилия6 Имя6 Отчество6',
                   6: 'Фамилия7 Имя7 Отчество7',
                   7: 'Фамилия8 Имя8 Отчество8',
                   8: 'Фамилия9 Имя9 Отчество9'}

def send_passer_name(conn, message):
    message = message.encode('utf-8')
    for i in range(len(message)):
        conn.send(bytes(divmod(BP.passing(message[i]), 256)))
    conn.send(bytes(divmod(BP.passing(0), 256)))

def threaded_client(conn):
    try:
        while True:
            #data = [BP.decode(i) for i in conn.recv()]
            data = conn.recv()
            data = data[0] * 256 + data[1]
            data = BP.decode(data)
            print('Received data:', data)
            send_passer_name(conn, pseudo_database[data])
    except RuntimeError as e:
        print(e)
    #except Exception as e:
        #print('Exception caught')
        #print(e)
    finally:
        conn.close()

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 9090))
    sock.listen(3)

    while True:
        conn, addr = sock.accept()
        conn.settimeout(10)
        conn = FLSocket(2, conn)
        print('Connected: ', addr)

        start_new_thread(threaded_client, (conn,))
