import errno
import functools
import tornado.ioloop as ioloop
import socket
import libopenflow as of

import Queue

fd_map = {}
message_queue_map = {}
fd_dict = {} #[control : sw; sw : control]

def handle_connection(connection, address):
        print "1 connection,", connection, address

def control(address, fd, events):
    sock = fd_map[fd]
    if events & io_loop.READ:
        print "msg from controller"
        data = sock.recv(1024)
        if data == '':
            print "controller disconnected"
            io_loop.remove_handler(fd)
        else:
            rmsg = of.ofp_header(data)
            print "msg from controller", rmsg
            rmsg.show()
            io_loop.update_handler(fd_dict[fd], io_loop.WRITE)
            message_queue_map[fd_map[fd_dict[fd]]].put(str(data))

    if events & io_loop.WRITE:
        print "trying to send packet to controller" 
        try:
            next_msg = message_queue_map[sock].get_nowait()
        except Queue.Empty:
            #print "%s queue empty" % str(address)
            io_loop.update_handler(fd, io_loop.READ)
        else:
            #print 'sending "%s" to %s' % (of.ofp_header(next_msg).type, address)
            sock.send(next_msg)

def client_handler(address, fd, events):
    sock = fd_map[fd]
    #print sock, sock.getpeername(), sock.getsockname()
    if events & io_loop.READ:
        data = sock.recv(1024)
        if data == '':
            print "connection dropped", sock, fd, sock.getpeername(), sock.getsockname()
            io_loop.remove_handler(fd)
        else:
            print "received something"
            io_loop.update_handler(fd_dict[fd], io_loop.WRITE)
            message_queue_map[fd_map[fd_dict[fd]]].put(str(data))

    if events & io_loop.WRITE:
        try:
            next_msg = message_queue_map[sock].get_nowait()
        except Queue.Empty:
            #print "%s queue empty" % str(address)
            io_loop.update_handler(fd, io_loop.READ)
        else:
            #print 'sending "%s" to %s' % (of.ofp_header(next_msg).type, address)
            sock.send(next_msg)

def agent(sock, fd, events):
    #TODO: create a new class for switches. when a switch connected to agent, new class
    #also, the sw is connected to controller using another socket.
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
    #switch = connection.fileno()
    client_handle = functools.partial(client_handler, address)
    io_loop.add_handler(connection.fileno(), client_handle, io_loop.READ)
    print "agent: connected to switch", connection.fileno(), client_handle
    message_queue_map[connection] = Queue.Queue()
    
    
    sock_control = new_sock(1)#no idea why, but when not blocking, it says: error: [Errno 36] Operation now in progress
    try:#look at: http://bbs.csdn.net/topics/230007709
        #it says such way can avoid error?
        sock_control.connect(("10.2.30.198",6633))#controller's IP
    except socket.error, e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN, errno.EINPROGRESS):
            raise
        return
    fd_map[sock_control.fileno()] = sock_control
    switch_handler = functools.partial(control, address)
    io_loop.add_handler(sock_control.fileno(), switch_handler, io_loop.READ)
    print "agent: connected to controller"
    message_queue_map[sock_control] = Queue.Queue()
    fd_dict[connection.fileno()] = sock_control.fileno()
    fd_dict[sock_control.fileno()] = connection.fileno()

def new_sock(block):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(block)
    return sock


sock = new_sock(0)
sock.bind(("", 6633))
sock.listen(6633)

io_loop = ioloop.IOLoop.instance()
#callback = functools.partial(connection_ready, sock)
callback = functools.partial(agent, sock)
print sock, sock.getsockname()
io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
io_loop.start()
