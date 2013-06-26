import errno
import functools
import tornado.ioloop as ioloop
import tornado.iostream as iostream
import socket
import libopenflow as of

import Queue

fd_map = {}
message_queue_map = {}

def handle_connection(connection, address):
        print "1 connection,", connection, address


def client_handler(address, fd, events):
    sock = fd_map[fd]
    #print sock, sock.getpeername(), sock.getsockname()
    if events & io_loop.READ:
        data = sock.recv(1024)
        if data:
            rmsg = of.ofp_header(data)
            print "received", rmsg.type, "from host."
            #rmsg.show()
            if rmsg.type == 0:
                print "OFPT_HELLO"
                msg = of.ofp_header(type = 5)
                io_loop.update_handler(fd, io_loop.WRITE)
                message_queue_map[sock].put(data)
                message_queue_map[sock].put(str(msg))
            if rmsg.type == 6:
                print "OFPT_FEATURES_REPLY"
                rmsg.show()

    if events & io_loop.WRITE:
        try:
            next_msg = message_queue_map[sock].get_nowait()
        except Queue.Empty:
            print "%s queue empty" % str(address)
            io_loop.update_handler(fd, io_loop.READ)
        else:
            print 'sending "%s" to %s' % (next_msg, address)
            sock.send(next_msg)

def agent(sock, fd, events):
    #print fd, sock, events
    try:
        connection, address = sock.accept()
    except socket.error, e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return
    connection.setblocking(0)
    handle_connection(connection, address)
    fd_map[connection.fileno()] = connection
    client_handle = functools.partial(client_handler, address)
    io_loop.add_handler(connection.fileno(), client_handle, io_loop.READ)
    message_queue_map[connection] = Queue.Queue()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(0)
sock.bind(("", 6633))
sock.listen(6633)

io_loop = ioloop.IOLoop.instance()
#callback = functools.partial(connection_ready, sock)
callback = functools.partial(agent, sock)
print sock, sock.getsockname()
io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
io_loop.start()
