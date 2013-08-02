"""
In this agent, the Tornado TCP server will use one process to manage all the classes.
Therefore, the total throughput of this script will be affected.  
"""
import errno
import functools
import tornado.ioloop as ioloop
import socket
import libopenflow as of

import Queue

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

"""
The switch class maintains the connection between controller and individual 
switches. For each OpenFlow switch, this transparent agent create a object of this 
class. 
"""
class switch():
    def __init__(self, sock_sw, sock_con):
        self.sock_sw    = sock_sw
        self.sock_con   = sock_con
        self.fd_sw      = sock_sw.fileno()
        self.fd_con     = sock_con.fileno()
        self.queue_con  = Queue.Queue()
        self.queue_sw   = Queue.Queue()
        self.buffer     = {}
        
    def controller_handler(self, address, fd, events):
        if events & io_loop.READ:
            data = self.sock_con.recv(1024)
            if data == '':
                print "controller disconnected"
                io_loop.remove_handler(self.fd_con)
                print "closing connection to switch"
                self.sock_sw.close()
                io_loop.remove_handler(self.fd_sw)
            else:
                rmsg = of.ofp_header(data[0:8])
                # Here, we can manipulate OpenFlow packets from CONTROLLER.
                #rmsg.show()
                if rmsg.type == 14:
                    #print "packet out/flow mod"
                    header = of.ofp_header(data[0:8])
                    wildcards = of.ofp_flow_wildcards(data[8:12])
                    match = of.ofp_match(data[12:48])
                    flow_mod = of.ofp_flow_mod(data[48:])
                    #print flow_mod.buffer_id, flow_mod.buffer_id == self.buffer[match.in_port]
                
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
                #print 'sending "%s" to %s' % (of.ofp_type[of.ofp_header(next_msg).type], self.sock_con.getpeername())
                self.sock_con.send(next_msg)

    def switch_handler(self, address, fd, events):
        if events & io_loop.READ:
            data = self.sock_sw.recv(1024)
            if data == '':
                print "switch disconnected"
                io_loop.remove_handler(self.fd_sw)
                print "closing connection to controller"
                self.sock_con.close()
                io_loop.remove_handler(self.fd_con)
            else:
                rmsg = of.ofp_header(data)
                #rmsg.show()
                if rmsg.type == 10:
                    #print "Packet In"
                    pkt_in_msg = of.ofp_packet_in(data[8:18])
                    #pkt_in_msg.show()
                    pkt_parsed = of.Ether(data[18:])
                    #pkt_parsed.show()
                    if isinstance(pkt_parsed.payload, of.IP) or isinstance(pkt_parsed.payload.payload, of.IP):
                        if isinstance(pkt_parsed.payload.payload, of.ICMP):
                            self.buffer[pkt_in_msg.in_port] = pkt_in_msg.buffer_id # bind buffer id with in port 
                            #print "ping", self.buffer  
                        elif isinstance(pkt_parsed.payload.payload.payload, of.ICMP):
                            self.buffer[pkt_in_msg.in_port] = pkt_in_msg.buffer_id # bind buffer id with in port 
                            #print "ping", self.buffer
                    
                # Here, we can manipulate OpenFlow packets from SWITCH.
                io_loop.update_handler(self.fd_con, io_loop.WRITE)
                self.queue_con.put(str(data))
    
        if events & io_loop.WRITE:
            try:
                next_msg = self.queue_sw.get_nowait()
            except Queue.Empty:
                #print "%s queue empty" % str(address)
                io_loop.update_handler(self.fd_sw, io_loop.READ)
            else:
                #print 'sending "%s" to %s' % (of.ofp_type[of.ofp_header(next_msg).type], self.sock_sw.getpeername())
                self.sock_sw.send(next_msg)

"""
For the callback function of socket listening, the agent function will first
try to accept the connection started by switch. And if the connection is successful,
this function will continue on creating another socket to connect the controller.
If the controller cannot be reached, there will be ``ECONNREFUSED`` error. 

After all these things are done, we will have two sockets, one from OpenFlow switch, another 
one to controller. Send these two sockets as parameter, a new switch object can be 
created. Before exit the agent function, this function will add ``new_switch.switch_handler``
and ``new_switch.controller_handler`` to callback function of their own socket.
"""
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
        sock_control.connect(("10.2.31.80",6633))#controller's IP, better change it into an argument
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
    controller_handler = functools.partial(new_switch.controller_handler, address)
    io_loop.add_handler(sock_control.fileno(), controller_handler, io_loop.READ)
    print "agent: connected to controller"
    
    switch_handler = functools.partial(new_switch.switch_handler, address)
    io_loop.add_handler(connection.fileno(), switch_handler, io_loop.READ)
    print "agent: connected to switch", num

if __name__ == '__main__':
    """
    For Tornado, there usually is only one thread, listening to the socket
    below. And also, this code block uses ``ioloop.add_handler()`` function
    to register a callback function if ``ioloop.READ`` event happens.
    
    When a new request from of switch, it will trigger ``ioloop.READ`` event
    in Tornado. And Tornado will execute the callback function ``agent()``.
    """
    sock = new_sock(0)
    sock.bind(("", 6633))
    sock.listen(6633)
    num = 0
    io_loop = ioloop.IOLoop.instance()
    callback = functools.partial(agent, sock)
    print sock, sock.getsockname()
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    io_loop.start()