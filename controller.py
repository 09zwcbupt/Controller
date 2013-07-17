import errno
import functools
import tornado.ioloop as ioloop
import socket
import libopenflow as of

import Queue
import time

fd_map = {}
message_queue_map = {}
pkt_out = of.ofp_header()/of.ofp_pktout_header()/of.ofp_action_output()
cookie = 0

def handle_connection(connection, address):
        print "1 connection,", connection, address

def client_handler(address, fd, events):
    sock = fd_map[fd]
    #print sock, sock.getpeername(), sock.getsockname()
    if events & io_loop.READ:
        data = sock.recv(1024)
        if data == '':
            """
            According to stackoverflow(http://stackoverflow.com/questions/667640/how-to-tell-if-a-connection-is-dead-in-python)
            When a socket is closed, the server will receive a EOF. In python, however, server will
            receive a empty string(''). So, when a switch disconnected, the server will find out
            at once. But, if you do not react on this incident, there will be always a ``ioloop.read``
            event. And the loop will run forever, thus, the CPU useage will be pretty high.
            """
            print "connection dropped"
            io_loop.remove_handler(fd)
        if len(data)<8:
            print "not a openflow message"
        else:
            #print len(data)
            #if the data length is 8, then only of header
            #else, there are payload after the header
            if len(data)>8:
                rmsg = of.ofp_header(data[0:8])
                body = data[8:]
            else:
                rmsg = of.ofp_header(data)
            #rmsg.show()
            if rmsg.type == 0:
                print "OFPT_HELLO"
                msg = of.ofp_header(type = 5)
                io_loop.update_handler(fd, io_loop.WRITE)
                message_queue_map[sock].put(data)
                message_queue_map[sock].put(str(msg))
            elif rmsg.type == 1:
                print "OFPT_ERROR"
            elif rmsg.type == 5:
                print "OFPT_FEATURES_REQUEST"
            elif rmsg.type == 6:
                print "OFPT_FEATURES_REPLY"
                #print "rmsg.load:",len(body)/48
                msg = of.ofp_features_reply(body[0:24])#length of reply msg
                #msg.show()
                port_info_raw = body[24:]
                port_info = {}
                print "port number:",len(port_info_raw)/48, "total length:", len(port_info_raw)
                for i in range(len(port_info_raw)/48):
                    #print "port", i, ",len:", len(port_info_raw[0+i*48:48+i*48]) 
                    """The port structure has a length of 48 bytes.
                       so when receiving port info, first split the list
                       into port structure length and then analysis
                    """
                    port_info[i] = of.ofp_phy_port(port_info_raw[0+i*48:48+i*48])
                    #print port_info[i].port_name
                    #port_info[i].show()
                    #print port_info[i].OFPPC_PORT_DOWN

            elif rmsg.type == 2:
                print "OFPT_ECHO_REQUEST"
                msg = of.ofp_header(type=3, xid=rmsg.xid)
                io_loop.update_handler(fd, io_loop.WRITE)
                message_queue_map[sock].put(str(msg))
            elif rmsg.type == 3:
                print "OFPT_ECHO_REPLY"
            elif rmsg.type == 4:
                print "OFPT_VENDOR"
            elif rmsg.type == 6:
                print "OFPT_FEATURES_REPLY"
            elif rmsg.type == 7:
                print "OFPT_GET_CONFIG_REQUEST"
            elif rmsg.type == 8:
                print "OFPT_GET_CONFIG_REPLY"
            elif rmsg.type == 9:
                print "OFPT_SET_CONFIG"
            elif rmsg.type == 10:
                #print "OFPT_PACKET_IN"
                #rmsg.show()
                pkt_in_msg = of.ofp_packet_in(body)
                #pkt_in_msg.show()
                raw = pkt_in_msg.load
                pkt_parsed = of.Ether(raw)
                #pkt_parsed.payload.show()
                #print "to see if the payload of ether is IP"
                #if isinstance(pkt_parsed.payload, of.IP):
                    #pkt_parsed.show()
                if isinstance(pkt_parsed.payload, of.ARP):
                    #pkt_parsed.show()
                    #pkt_out = of.ofp_header()/of.ofp_pktout_header()/of.ofp_action_output()
                    pkt_out.payload.payload.port = 0xfffb
                    pkt_out.payload.buffer_id = pkt_in_msg.buffer_id
                    pkt_out.payload.in_port = pkt_in_msg.in_port
                    pkt_out.length = 24
                    #pkt_out.show()
                    io_loop.update_handler(fd, io_loop.WRITE)
                    message_queue_map[sock].put(str(pkt_out))
                if isinstance(pkt_parsed.payload, of.IP):
                    if isinstance(pkt_parsed.payload.payload, of.ICMP):
                        print "from", pkt_parsed.src, "to", pkt_parsed.dst 
                        
                        """
                        When receive a OPF_PACKET_IN message, you can caculate a path, and then
                        use OFP_FLOW_MOD message to install path. Also, you can find out the exact
                        port to send the message, then you can use the following code to send a
                        OFP_PACKET_OUT message and send the packet to destination.
                        """
                        """
                        #pkt_parsed.show()
                        #pkt_out = of.ofp_header()/of.ofp_pktout_header()/of.ofp_action_output()
                        pkt_out.payload.payload.port = 0xfffb
                        pkt_out.payload.buffer_id = pkt_in_msg.buffer_id
                        pkt_out.payload.in_port = pkt_in_msg.in_port
                        pkt_out.length = 24
                        """
                        """
                        io_loop.update_handler(fd, io_loop.WRITE)
                        message_queue_map[sock].put(str(pkt_out))
                        """
                        
                        #print pkt_parsed.payload.proto
                        #pkt_parsed.show()
                        #print "ICMP protocol"
                        #pkt_out.show()
                        #usually don't have to fill in ``wilecards`` area 
                        global cookie
                        cookie += 1
                        flow_mod_msg = of.ofp_header(type=14,
                                                     length=80)/\
                        of.ofp_flow_wildcards()\
                        /of.ofp_match(in_port=pkt_in_msg.in_port,
                                      dl_src=pkt_parsed.src,
                                      dl_dst=pkt_parsed.dst,
                                      dl_type=pkt_parsed.type,
                                      nw_tos=pkt_parsed.payload.tos,
                                      nw_proto=pkt_parsed.payload.proto,
                                      nw_src=pkt_parsed.payload.src,
                                      nw_dst=pkt_parsed.payload.dst,
                                      tp_src = pkt_parsed.payload.payload.type,
                                      tp_dst = pkt_parsed.payload.payload.code)\
                        /of.ofp_flow_mod(cookie=cookie,
                                         command=0,
                                         idle_timeout=60,
                                         buffer_id=pkt_in_msg.buffer_id,#icmp type 8: request, 0: reply
                                         flags=1)\
                        /of.ofp_action_output(type=0, 
                                              port=0xfffb,
                                              len=8)
                        """flow_mod_msg.show()
                        
                        print "--------------------------------------------------------------------------------------"
                        print "len of flow_mod_msg        :", len(str(flow_mod_msg))
                        print "len of of_header()         :", len(str(of.ofp_header()))
                        print "len of ofp_flow_wildcards():", len(str(of.ofp_flow_wildcards()))
                        print "len of ofp_match()         :", len(str(of.ofp_match()))
                        print "len of ofp_flow_mod()      :", len(str(of.ofp_flow_mod(command=0,idle_timeout=60,buffer_id=pkt_in_msg.buffer_id)))
                        print "len of ofp_action_output() :", len(str(of.ofp_action_output(type=0,port=0xfffb,len=8)))
                        print "--------------------------------------------------------------------------------------"
                        """
                        io_loop.update_handler(fd, io_loop.WRITE)
                        #message_queue_map[sock].put(str(pkt_out))
                        message_queue_map[sock].put(str(flow_mod_msg))
                #io_loop.stop()

            elif rmsg.type == 11: 
                print "OFPT_FLOW_REMOVED"
            elif rmsg.type == 12:
                print "OFPT_PORT_STATUS"
            elif rmsg.type == 13:
                print "OFPT_PACKET_OUT"
            elif rmsg.type == 14:
                print "OFPT_FLOW_MOD"
            elif rmsg.type == 15:
                print "OFPT_PORT_MOD"
            elif rmsg.type == 16:
                print "OFPT_STATS_REQUEST"
            elif rmsg.type == 17:
                print "OFPT_STATS_REPLY"
            
            # no message body
            elif rmsg.type == 18:
                print "OFPT_BARRIER_REQUEST"
            
            #no message body
            elif rmsg.type == 19:
                print "OFPT_BARRIER_REPLY: ", rmsg.xid, "Successful"
            elif rmsg.type == 20:
                print "OFPT_QUEUE_GET_CONFIG_REQUEST"
            elif rmsg.type == 21:
                print "OFPT_QUEUE_GET_CONFIG_REPLY"

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
    print "in agent: new switch", connection.fileno(), client_handle
    message_queue_map[connection] = Queue.Queue()

def new_sock(block):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(block)
    return sock

if __name__ == '__main__':
    sock = new_sock(0)
    sock.bind(("", 6633))
    sock.listen(6633)
    
    io_loop = ioloop.IOLoop.instance()
    #callback = functools.partial(connection_ready, sock)
    callback = functools.partial(agent, sock)
    print sock, sock.getsockname()
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
        print "quit"