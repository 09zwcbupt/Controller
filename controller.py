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
            #print "received", rmsg.type, "from host."
            #rmsg.show()
            if rmsg.type == 0:
                print "OFPT_HELLO"
                msg = of.ofp_header(type = 5)
                io_loop.update_handler(fd, io_loop.WRITE)
                message_queue_map[sock].put(data)
                message_queue_map[sock].put(str(msg))
            if rmsg.type == 1:
                print "OFPT_ERROR"
            if rmsg.type == 5:
                print "OFPT_FEATURES_REQUEST"
            if rmsg.type == 6:
                print "OFPT_FEATURES_REPLY"
                rmsg.show()
                #print "rmsg.load:",rmsg.load
                port_info = of.ofp_phy_port(rmsg.load)
                port_info.show()
            if rmsg.type == 2:
                print "OFPT_ECHO_REQUEST"
            if rmsg.type == 3:
                print "OFPT_ECHO_REPLY"
            if rmsg.type == 4:
                print "OFPT_VENDOR"
            if rmsg.type == 6:
                print "OFPT_FEATURES_REPLY"
            if rmsg.type == 7:
                print "OFPT_GET_CONFIG_REQUEST"
            if rmsg.type == 8:
                print "OFPT_GET_CONFIG_REPLY"
            if rmsg.type == 9:
                print "OFPT_SET_CONFIG"
            if rmsg.type == 10:
                print "OFPT_PACKET_IN"
            if rmsg.type == 11: 
                print "OFPT_FLOW_REMOVED"
            if rmsg.type == 12:
                print "OFPT_PORT_STATUS"
            if rmsg.type == 13:
                print "OFPT_PACKET_OUT"
            if rmsg.type == 14:
                print "OFPT_FLOW_MOD"
            if rmsg.type == 15:
                print "OFPT_PORT_MOD"
            if rmsg.type == 16:
                print "OFPT_STATS_REQUEST"
            if rmsg.type == 17:
                print "OFPT_STATS_REPLY"
            if rmsg.type == 18:
                print "OFPT_BARRIER_REQUEST"
            if rmsg.type == 19:
                print "OFPT_BARRIER_REPLY"
            if rmsg.type == 20:
                print "OFPT_QUEUE_GET_CONFIG_REQUEST"
            if rmsg.type == 21:
                print "OFPT_QUEUE_GET_CONFIG_REPLY"

    if events & io_loop.WRITE:
        try:
            next_msg = message_queue_map[sock].get_nowait()
        except Queue.Empty:
            print "%s queue empty" % str(address)
            io_loop.update_handler(fd, io_loop.READ)
        else:
            print 'sending "%s" to %s' % (of.ofp_header(next_msg).type, address)
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
