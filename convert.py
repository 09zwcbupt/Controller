# convert from ofp -> ofcp
# or back from ofcp -> ofp

import libopenflow as of
import libopencflow as ofc

def of2ofc(msg, buffer, dpid):
    print "converting"
    if isinstance(msg, of.ofp_header):
        if isinstance(msg.payload, of.ofp_packet_in):
            # Save the buffer_id from pkt_in message. As 1. of.pkt_out message needs buffer_id
            # 2. the in_port is only one kind of pkt, this method seems okay in linear or ring topo
            
            #only need the ofp_header()/ofp_packet_in() part of the msg
            print "packet in from port", msg.payload.in_port
            buffer[msg.payload.in_port] = msg.payload.buffer_id
            #print buffer_id
        if isinstance(msg.payload, of.ofp_flow_mod):
            #basic structure: of.ofp_header()/of.ofp_flow_wildcards()/of.ofp_match()/of.ofp_flow_mod()/other_ofp_actions()
            #select info from match (VLAN) and actions (just copy)
            print "1"
    
    
def ofc2of(msg, buffer, dpid):
    print "converting"
    if isinstance(msg, ofc.ofp_header):
        if isinstance(msg.payload, ofc.ofp_cflow_mod):
            #self.buffer[(pkt_in_msg.in_port, id)] = [pkt_in_msg.buffer_id, rmsg/pkt_in_msg/pkt_parsed]
            #basic structure: ofp_header()/ofp_cflow_mod()/ofp_connect_wildcards()/ofp_connect()/other_ofp_actions()
            #select info from connect (port info) and actions (just copy)
            #WDM: num_wave -> vlan id
            #OTN: supp_sw_otn_gran->different map function ; bitmap->calculate vlan id
            #ODU0 = 0, ODU1 = 1 ...
            
            # [port + id] --> [buffer_id + pkt_in_msg]
            #print buffer
            buffer_id, pkt = buffer[(msg.payload.payload.payload.in_port, msg.xid)]
            del buffer[(msg.payload.payload.payload.in_port, msg.xid)]
            pkt_parsed = pkt.payload.payload
            if isinstance(pkt_parsed.payload, of.IP) or isinstance(pkt_parsed.payload.payload, of.IP):
                    #print isinstance(pkt_parsed.payload, of.Dot1Q)
                    #print pkt_parsed.payload.vlan   
                    if isinstance(pkt_parsed.payload.payload.payload, of.ICMP):
                        #print "dpid:", sock_dpid[fd]
                        #pkt_parsed.show()
                        
                        flow_mod_msg = of.ofp_header(type=14,
                                                     length=88,)\
                                       /of.ofp_flow_wildcards(OFPFW_NW_TOS=1,
                                                              OFPFW_DL_VLAN_PCP=1,
                                                              OFPFW_NW_DST_MASK=1,
                                                              OFPFW_NW_SRC_MASK=1,
                                                              OFPFW_TP_DST=1,
                                                              OFPFW_TP_SRC=1,
                                                              OFPFW_NW_PROTO=1,
                                                              OFPFW_DL_TYPE=1,
                                                              OFPFW_DL_VLAN=0,
                                                              OFPFW_IN_PORT=0,
                                                              OFPFW_DL_DST=0,
                                                              OFPFW_DL_SRC=0)\
                                       /of.ofp_match(in_port=msg.payload.payload.payload.in_port,
                                                     dl_src=pkt_parsed.src,
                                                     dl_dst=pkt_parsed.dst,
                                                     dl_type=pkt_parsed.type,
                                                     dl_vlan=pkt_parsed.payload.vlan,
                                                     nw_tos=pkt_parsed.payload.tos,
                                                     nw_proto=pkt_parsed.payload.proto,
                                                     nw_src=pkt_parsed.payload.src,
                                                     nw_dst=pkt_parsed.payload.dst,
                                                     tp_src = pkt_parsed.payload.payload.type,
                                                     tp_dst = pkt_parsed.payload.payload.code)\
                                       /of.ofp_flow_mod(cookie=0,
                                                        command=0,
                                                        idle_timeout=0,
                                                        hard_timeout=60,
                                                        buffer_id=buffer_id,#icmp type 8: request, 0: reply
                                                        flags=1)
                        
                        if (not isinstance(pkt_parsed.payload, of.IP)) and pkt_parsed.payload.src =="10.0.0.1" and dpid == 2: # have VLAN and from node 2 -> 1 @s2 (rm vlan)
                            print "1->2 @s2"
                            flow_mod_msg = flow_mod_msg/of.ofp_action_header(type=3)/of.ofp_action_output(type=0, port=0xfffb, len=8)
                        
                        elif (not isinstance(pkt_parsed.payload, of.IP)) and pkt_parsed.payload.src =="10.0.0.2" and dpid == 1: # have VLAN and from node 2 -> 1 (rm vlan)
                            print "1<-2 @s1"
                            flow_mod_msg = flow_mod_msg/of.ofp_action_header(type=3)/of.ofp_action_output(type=0, port=0xfffb, len=8)
                        
                        #flow_mod_msg.show()
                        return flow_mod_msg
                    elif isinstance(pkt_parsed.payload.payload, of.ICMP):
                        
                        flow_mod_msg = of.ofp_header(type=14,
                                                     length=88,)\
                                       /of.ofp_flow_wildcards()\
                                       /of.ofp_match(in_port=msg.payload.payload.payload.in_port,
                                                     dl_src=pkt_parsed.src,
                                                     dl_dst=pkt_parsed.dst,
                                                     dl_type=pkt_parsed.type,
                                                     nw_tos=pkt_parsed.payload.tos,
                                                     nw_proto=pkt_parsed.payload.proto,
                                                     nw_src=pkt_parsed.payload.src,
                                                     nw_dst=pkt_parsed.payload.dst,
                                                     tp_src = pkt_parsed.payload.payload.type,
                                                     tp_dst = pkt_parsed.payload.payload.code)\
                                       /of.ofp_flow_mod(cookie=0,
                                                        command=0,
                                                        idle_timeout=0,
                                                        hard_timeout=60,
                                                        buffer_id=buffer_id,#icmp type 8: request, 0: reply
                                                        flags=1)
                                       
                        # h1 -> (add vlan)of_switch(rm vlan) -> h2
                        if isinstance(pkt_parsed.payload, of.IP) and pkt_parsed.payload.src == "10.0.0.1" and dpid == 1: # not VLAN and from node 1 -> 2 @s1(add vlan)
                            print "1->2 @s1"
                            flow_mod_msg = flow_mod_msg/of.ofp_action_vlan_vid(vlan_vid = 100)/of.ofp_action_output(type=0, port=0xfffb, len=8)                            
                        
                        # h1 <- (rm vlan)of_switch(add vlan) <- h2
                        elif isinstance(pkt_parsed.payload, of.IP) and pkt_parsed.payload.src == "10.0.0.2" and dpid == 2: # not VLAN and from node 1 -> 2 @s2(add vlan)
                            print "1<-2 @s2"
                            flow_mod_msg = flow_mod_msg/of.ofp_action_vlan_vid(vlan_vid = 200)/of.ofp_action_output(type=0, port=0xfffb, len=8)
                        #flow_mod_msg.show()
                        return flow_mod_msg
                            
buffer_id = {}

of2ofc_dict = {
               }

ofc2of_dict_odu = { 0: lambda x:x+2000,
                    1: lambda x:x+2100,
                    2: lambda x:x+2200,
                    3: lambda x:x+2300}

ofc2of_dict_wave = lambda x:x+3000
        
#of.ofp_header().show()
#ofc.ofp_header().show()

if __name__ == "__main__":
    # this convert (can) only match in-coming port and vlan
    
    # 1. packet_in message
    pkt_in_msg = of.ofp_header(type=14,length=88)/of.ofp_packet_in(in_port=1,buffer_id=128, total_len=10)
    #pkt_in_msg.show()
    of2ofc(pkt_in_msg, buffer_id) # get buffer_id
    
    ofc_pkt = ofc.ofp_header()\
          /ofc.ofp_cflow_mod()\
          /ofc.ofp_connect_wildcards()\
          /ofc.ofp_connect(nport_in=1, supp_sw_otn_gran_in=1, in_port=1)\
          /of.ofp_action_header(type=3)\
          /of.ofp_action_output(type=0, port=0xfffb, len=8)
    #ofc_pkt.show()
    print buffer_id
    # 2. parse ofc message
    of_pkt = ofc2of(ofc_pkt, buffer_id)
    
    # 3. print of message
    of_pkt.show()
    
    """
    print ofc2of_dict_odu[0](1)
    print ofc2of_dict_odu[0](30)
    print ofc2of_dict_odu[1](1)
    print ofc2of_dict_odu[2](1)
    print ofc2of_dict_odu[3](1)
    
    print ofc2of_dict_wave(80)
    """