from socket import socket, AF_INET, SOCK_STREAM

class FLSocket:

    def __init__(self, MSGLEN, sock=None):
        self.sock = sock if sock else socket(AF_INET, SOCK_STREAM)
        self.MSGLEN = MSGLEN

    def connect(self, host, port):
        self.sock.connect((host, port))
       
    def send(self, msg):
        totalsent = 0
        while totalsent < self.MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if not sent:
                raise RuntimeError("socket connection broken")
            totalsent += sent

    def recv(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < self.MSGLEN:
            chunk = self.sock.recv(min(self.MSGLEN - bytes_recd, self.MSGLEN))
            if not chunk:
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd += len(chunk)
            return b''.join(chunks)

    def close(self):
        self.sock.close()
