import errno
import functools
import tornado.ioloop as ioloop
import socket
import libopenflow as of

import Queue

fd_map = {}
message_queue_map = {}
fd_dict = {} #[control : sw; sw : control]

#create a connection between socket fd of (controller, sw) and sw class 
fdmap = {}
num = 0

"""
Print connection information
"""
def print_connection(connection, address):
        print "connection:", connection, address

"""
Create a new socket
The parameter ``block`` determine if the return socket is blocking
or nonblocking socket. Use '1' when creating a socket which connect
a controller.
"""
def new_sock(block):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(block)
    return sock

class switch():
    def __init__(self, sock_sw, sock_con):
        self.sock_sw    = sock_sw
        self.sock_con   = sock_con
        self.fd_sw      = sock_sw.fileno()
        self.fd_con     = sock_con.fileno()
        self.queue_con  = Queue.Queue()
        self.queue_sw   = Queue.Queue()
        
    def control(self, address, fd, events):
        if events & io_loop.READ:
            data = self.sock_con.recv(1024)
            if data == '':
                print "controller disconnected"
                io_loop.remove_handler(self.fd_con)
                print "closing connection to switch"
                self.sock_sw.close()
                io_loop.remove_handler(self.fd_sw)
            else:
                rmsg = of.ofp_header(data)
                #print "msg from controller", rmsg
                #rmsg.show()
                io_loop.update_handler(self.fd_sw, io_loop.WRITE)
                self.queue_sw.put(str(data))
    
        if events & io_loop.WRITE:
            #print "trying to send packet to controller" 
            try:
                next_msg = self.queue_con.get_nowait()
            except Queue.Empty:
                #print "%s queue empty" % str(address)
                io_loop.update_handler(self.fd_con, io_loop.READ)
            else:
                print 'sending "%s" to %s' % (of.ofp_type[of.ofp_header(next_msg).type], self.sock_con.getpeername())
                self.sock_con.send(next_msg)

    def client_handler(self, address, fd, events):
        #print sock, sock.getpeername(), sock.getsockname()
        if events & io_loop.READ:
            data = self.sock_sw.recv(1024)
            if data == '':
                print "switch disconnected"#, sock, self.fd_sw, sock.getpeername(), sock.getsockname()
                io_loop.remove_handler(self.fd_sw)
                print "closing connection to controller"
                self.sock_con.close()
                io_loop.remove_handler(self.fd_con)
            else:
                #print "received something"
                io_loop.update_handler(self.fd_con, io_loop.WRITE)
                self.queue_con.put(str(data))
    
        if events & io_loop.WRITE:
            try:
                next_msg = self.queue_sw.get_nowait()
            except Queue.Empty:
                #print "%s queue empty" % str(address)
                io_loop.update_handler(self.fd_sw, io_loop.READ)
            else:
                print 'sending "%s" to %s' % (of.ofp_type[of.ofp_header(next_msg).type], self.sock_sw.getpeername())
                self.sock_sw.send(next_msg)

def agent(sock, fd, events):
    #TODO: create a new class for switches. when a switch connected to agent, new class
    #also, the sw is connected to controller using another socket.
    #print fd, sock, events
    
    #1. accept connection from switch
    try:
        connection, address = sock.accept()
    except socket.error, e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return
    connection.setblocking(0)
    
    #2. connecting to controller
    #no idea why, but when not blocking, it says: error: [Errno 36] Operation now in progress
    sock_control = new_sock(1)
    try:
        sock_control.connect(("10.2.30.198",6633))#controller's IP
    except socket.error, e:
        if e.args[0] not in (errno.ECONNREFUSED, errno.EINPROGRESS):
            raise
        if e.args[0] == errno.ECONNREFUSED:
            print "cannot establish connection to controller, please check your config."
        return
    sock_control.setblocking(0)
    
    #3. create sw class object
    global num
    num = num + 1
    new_switch = switch(connection, sock_control)
    print "switch instance No.", num
    fdmap[connection.fileno()] = new_switch
    fdmap[sock_control.fileno()] = new_switch
    
    #print_connection(connection, address)
    #print_connection(sock_control, sock_control.getpeername())
    #fd_map[connection.fileno()] = connection
    #switch = connection.fileno()
    client_handle = functools.partial(new_switch.client_handler, address)
    io_loop.add_handler(connection.fileno(), client_handle, io_loop.READ)
    print "agent: connected to switch", num#, connection.fileno(), client_handle
    #message_queue_map[connection] = Queue.Queue()
    
    #fd_map[sock_control.fileno()] = sock_control
    switch_handler = functools.partial(new_switch.control, address)
    io_loop.add_handler(sock_control.fileno(), switch_handler, io_loop.READ)
    print "agent: connected to controller"
    #message_queue_map[sock_control] = Queue.Queue()
    #fd_dict[connection.fileno()] = sock_control.fileno()
    #d_dict[sock_control.fileno()] = connection.fileno()

if __name__ == '__main__':
    sock = new_sock(0)
    sock.bind(("", 6633))
    sock.listen(6633)
    num = 0
    io_loop = ioloop.IOLoop.instance()
    #callback = functools.partial(connection_ready, sock)
    callback = functools.partial(agent, sock)
    print sock, sock.getsockname()
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    io_loop.start()
