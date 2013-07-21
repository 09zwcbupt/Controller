import Queue
import socket
import libopenflow as of
from functools import partial
from tornado.ioloop import IOLoop
import threading

fd_map = {}              
event_map = {}
thread_map = {}

class switch(threading.Thread):
    def __init__(self, sock, event):
        print "init for connection", sock.fileno()
        self.sock = sock # for sending pkts
        self.event = event # for waiting pkt_in
        self._quit = False
        super(switch, self).__init__()
        
    def run(self):
        while not self._quit:
            print "waiting", sock.getsockname()
            #sock.send("123")
            self.event.wait() #waiting for a packet
            if self._quit:
                print "receive quit signal"
                self.event.clear()
                return
            #need something to ?
            #print self.sock, self.sock.getsockname(), self.sock.getpeername()
            #try:
            data = self.sock.recv(1024)
            print len(data), data
            if len(data)>=8:
                msg = of.ofp_header(data)
                msg.show()
                if msg.type == 0:
                    print "OFP_HELLO"
                    self.sock.send(data)
            #except 
            #data = ""
            if data == "":
                print "close connection"
                sock.close()
                return
            self.sock.send(data)
            self.event.clear()
        print "quit", self._quit

    def stop(self):
        print "closing thread & connection" 
        self.sock.close()
        self.event.set()
        self._quit = True
    
def handle_pkt(cli_addr, fd, event):
    s = fd_map[fd]
    if event & IOLoop.READ:
        #data = sock.recv(1024)
        event_map[s].set()
        #print s
        #ioloop.update_handler(fd, IOLoop.WRITE)
        #return
        
    if event & IOLoop.ERROR:
        print " exception on %s" % cli_addr
        ioloop.remove_handler(fd)
        s.close()
        #del message_queue_map[s]
    
    
def handle_server(sock, fd, event):
    s = fd_map[fd]
    try:
        conn, cli_addr = sock.accept()
    except socket.error, e:
        if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return
    #if event & IOLoop.READ:    
    print "connection %s" % cli_addr[0],s, conn.fileno(), conn
    print conn.getsockname(), conn.getpeername()
    conn.setblocking(0)
    conn_fd = conn.fileno()
    fd_map[conn_fd] = conn
    handle = partial(handle_pkt, conn)
    ioloop.add_handler(conn_fd, handle, IOLoop.READ)
    event_map[conn] = threading.Event()
    thread_map[conn_fd] = switch(conn, event_map[conn])
    print thread_map
    thread_map[conn_fd].start()

if __name__ == '__main__':
    ioloop = IOLoop.instance()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    server_address = ("localhost", 6633)
    sock.bind(server_address)
    sock.listen(5)
    fd = sock.fileno()
    fd_map[fd] = sock
    
    callback = partial(handle_pkt, sock)
    ioloop.add_handler(sock.fileno(), callback, ioloop.READ)
    #ioloop.add_handler(fd, handle_server, IOLoop.READ)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        print "quit"
        for t in thread_map:
            thread_map[t].stop()
            thread_map[t].join
        ioloop.stop()
        sock.close()