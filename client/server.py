from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from _thread import start_new_thread

def threaded_client(conn):
    data = ''
    while True:
        tmp_data = conn.recv(1024)
        print('Temporary: ' + tmp_data.decode('utf-8'))
        data += tmp_data.decode('utf-8')
        if not tmp_data:
            conn.send(data.encode('utf-8'))
            break
    conn.close()
    print('Data: ' + data)

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 9092))
    sock.listen(3)

    while True:
        conn, addr = sock.accept()
        conn.settimeout(10)
        print('Connected: ', addr)

        start_new_thread(threaded_client, (conn,))
