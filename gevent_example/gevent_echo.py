import gevent
from gevent import socket
from gevent.server import StreamServer
import libopenflow as of

def testing_of(pkt):
    print "handling packet"

def handle_echo(sock, address):
    fp = sock.makefile()
    while True:
        line = fp.readline()
        if line:
            #threads = [gevent.spawn(task, pkt)]
            gevent.joinall(threads)
            fp.write(line)
            fp.flush()
        else:
            break
    sock.shutdown(socket.SHUT_WR)
    sock.close()

server = StreamServer(
    ('', 6633), handle_echo)

server.serve_forever()
