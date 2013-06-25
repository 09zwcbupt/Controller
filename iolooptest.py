import errno
import functools
import tornado.ioloop as ioloop
import tornado.iostream as iostream
import socket
import openflow_header as of

def connection_ready(sock, fd, events):
    #while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        connection.setblocking(0)
        handle_connection(connection, address)
        stream = iostream.IOStream(connection)
        stream.read_bytes(8, print_on_screen)
        #generate a openflow message. by default, it's a OFP_HELLO msg
        msg = of.ofp_header()
        
        #the 'stream.write' needs string
        stream.write(str(msg))
        print "send OFP_HELLO"

def print_on_screen(data):
    print "received something"
    rmsg = of.ofp_header(data)
    rmsg.show()

def handle_connection(connection, address):
        print "1 connection,", connection, address

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(0)
sock.bind(("", 6633))
sock.listen(6633)

io_loop = ioloop.IOLoop.instance()
callback = functools.partial(connection_ready, sock)
io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
io_loop.start()
