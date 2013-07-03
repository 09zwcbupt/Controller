from gevent import socket
from gevent.server import StreamServer

def handle_echo(sock, address):
    fp = sock.makefile()
    while True:
        line = fp.readline()
        if line:
            fp.write(line)
            fp.flush()
        else:
            break
    sock.shutdown(socket.SHUT_WR)
    sock.close()

server = StreamServer(
    ('', 1234), handle_echo)

server.serve_forever()
