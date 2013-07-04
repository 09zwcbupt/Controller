import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')
from scapy.all import *

#uint8_t => XByteField
#uint16_t => ShortField, BitFieldLenField('name', None, 16, length_of='varfield')
#uint32_t => IntField, BitFieldLenField('name', None, 32, length_of='varfield'),

###################
# Data Structures #
###################

ofp_port = { 0xff00: "OFPP_MAX",
             0xfff8: "OFPP_IN_PORT",
             0xfff9: "OFPP_TABLE",
             0xfffa: "OFPP_NORMAL",
             0xfffb: "OFPP_FLOOD",
             0xfffc: "OFPP_ALL",
             0xfffd: "OFPP_CONTROLLER",
             0xfffe: "OFPP_LOCAL",
             0xffff: "OFPP_NONE"}

class ofp_phy_port(Packet):
    name = "OpenFlow Port"
    fields_desc=[ ShortEnumField("port_no", 0, ofp_port),
                  MACField("hw_addr", 0),
                  StrFixedLenField("port_name", None, length=16),
                  #StrField("port_name", None, fmt="H", remain=24),
                  #BitFieldLenField('port_name', None, 128, length_of='varfield'),

                  #TODO: still some problem with this part
                  #uint32_t for port config, for Openflow 1.0, this part only uses 7 bits.
                  BitField("not_defined", 0, 25),
                  BitField("OFPPC_NO_PACKET_IN", 0, 1),
                  BitField("OFPPC_NO_FWD", 0, 1),
                  BitField("OFPPC_NO_FLOOD", 0, 1),
                  BitField("OFPPC_NO_RECV_STP",0, 1),
                  BitField("OFPPC_NO_RECV", 0, 1),
                  BitField("OFPPC_NO_STP", 0, 1),
                  BitField("OFPPC_PORT_DOWN", 0, 1),
                  

                  #uint32_t for state
                  BitField("else", 0, 31),
                  BitField("OFPPS_LINK_DOWN", 0, 1),

                  #uint32_t for Current features
                  BitField("not_defined", 0, 20),
                  BitField("OFPPF_PAUSE_ASYM", 0, 1),
                  BitField("OFPPF_PAUSE", 0, 1),
                  BitField("OFPPF_AUTONEG", 0, 1),
                  BitField("OFPPF_FIBER", 0, 1),
                  BitField("OFPPF_COPPER", 0, 1),
                  BitField("OFPPF_10GB_FD", 0, 1),
                  BitField("OFPPF_1GB_FD", 0, 1),
                  BitField("OFPPF_1GB_HD", 0, 1),
                  BitField("OFPPF_100MB_FD", 0, 1),
                  BitField("OFPPF_100MB_HD", 0, 1),
                  BitField("OFPPF_10MB_FD", 0, 1),
                  BitField("OFPPF_10MB_HD", 0, 1),
                  
                  #uint32_t for features being advised by the port
                  BitField("advertised", 0, 32),

                  #uint32_t for features supported by the port
                  BitField("supported", 0, 32),

                  #uint32_t for features advertised by peer
                  BitField("peer", 0, 32)]

ofp_action_type = { 0: "OFPAT_OUTPUT",
                    1: "OFPAT_SET_VLAN_VID",
                    2: "OFPAT_SET_VLAN_PCP",
                    3: "OFPAT_STRIP_VLAN",
                    4: "OFPAT_SET_DL_SRC",
                    5: "OFPAT_SET_DL_DST",
                    6: "OFPAT_SET_NW_SRC",
                    7: "OFPAT_SET_NW_DST",
                    8: "OFPAT_SET_NW_TOS",
                    9: "OFPAT_SET_TP_SRC",
                    10: "OFPAT_SET_TP_DST",
                    11: "OFPAT_ENQUEUE",
                    0xffff: "OFPAT_VENDOR"}

class ofp_action_header(Packet):
    name = "OpenFlow Action Header"
    fields_desc=[ ShortEnumField("type", 0, ofp_action_type),
                  ShortField("len", 0), #length of this action (including this header)
                  XByteField("pad", 0)]

###################
# OpenFlow Header #
###################

ofp_type = { 0: "OFPT_HELLO",
             1: "OFPT_ERROR",
             2: "OFPT_ECHO_REQUEST",
             3: "OFPT_ECHO_REPLY",
             4: "OFPT_VENDOR",
             5: "OFPT_FEATURES_REQUEST",
             6: "OFPT_FEATURES_REPLY",
             7: "OFPT_GET_CONFIG_REQUEST",
             8: "OFPT_GET_CONFIG_REPLY",
             9: "OFPT_SET_CONFIG",
             10: "OFPT_PACKET_IN",
             11: "OFPT_FLOW_REMOVED",
             12: "OFPT_PORT_STATUS",
             13: "OFPT_PACKET_OUT",
             14: "OFPT_FLOW_MOD",
             15: "OFPT_PORT_MOD",
             16: "OFPT_STATS_REQUEST",
             17: "OFPT_STATS_REPLY",
             18: "OFPT_BARRIER_REQUEST",
             19: "OFPT_BARRIER_REPLY",
             20: "OFPT_QUEUE_GET_CONFIG_REQUEST",
             21: "OFPT_QUEUE_GET_CONFIG_REPLY"
             #Messages for circuit switched ports
             #255: "OFPT_CFLOW_MOD",
           }

class ofp_header(Packet):
    name = "OpenFlow Header "
    fields_desc=[ XByteField("version", 1),
                 ByteEnumField("type", 0, ofp_type),
                 ShortField("length", 8),
                 IntField("xid", 1) ]

#OFP_HELLO, OFP_ECHO_REQUEST and OFP_FEATURES_REQUEST do not have a body.

#####################
# OpenFlow Messages #
#####################

# No. 6
class ofp_features_reply(Packet):
    name = "OpenFlow Switch Features Reply"
    """
    If the field is number has some meaning, and have to use ``show()`` to present
    better not use things in Simple datatypes like ``LongField`` or ``IEEEDoubleField``
    those field will automatically convert your data into some unreadable numbers
    For presenting, just use ``BitFieldLenField``, parameters are name, default
    value, length(in bits) and something I don't know.
    """
    fields_desc=[ BitFieldLenField('datapath_id', None, 64, length_of='varfield'),
                  BitFieldLenField('n_buffers', None, 32, length_of='varfield'),
                  XByteField("n_tables", 0),
                  X3BytesField("pad", 0),
                  #features
                  BitFieldLenField('capabilities', None, 32, length_of='varfield'),
                  BitFieldLenField('actions', None, 32, length_of='varfield'),
                  #port info can be resoved at TCP server
                ]

bind_layers( ofp_header, ofp_features_reply, type=6 )

ofp_packet_in_reason = { 0: "OFPR_NO_MATCH",
                         1: "OFPR_ACTION",}
# No. 10
class ofp_packet_in(Packet):
    name = "OpenFlow Packet In"
    fields_desc=[ IntField("buffer_id", None),
                  ShortField("total_len", None),
                  ShortField("in_port", None),
                  ByteEnumField("reason", 0, ofp_packet_in_reason),
                  ByteField("pad", None)]
# No. 13
class ofp_action_header(Packet):
    name = "OpenFlow Packet Out"
    fields_desc=[ IntField("buffer_id", None),
                  ShortField("in_port", None),
                  ShortField("actions_len", None)] #size of action array in bytes
    #followed by actions

bind_layers( ofp_header, ofp_action_header, type=13)

class ofp_action_output(Packet):
    name = "OpenFLow Action Output"
    fields_desc=[ ShortEnumField("type", 0, ofp_action_type),
                  ShortField("len", 8),
                  ShortEnumField("port", None, ofp_port),
                  ShortField("max_len", 0)]

bind_layers( ofp_action_header, ofp_action_output, type=0)
bind_layers( ofp_action_header, ofp_action_output, actions_len=8)

if __name__ == '__main__':
    a = ofp_header()
    a.show()
    a.type = 3
    a.show()
    print 'can only change type to another number'
    a.tpye = "OFPT_STATS_REPLY"
    a.show()
    a.type = 17
    a.show()

    print "\n testing for the OFP_FEATURES_REPLY msg"
    b = ofp_header()/ofp_features_reply()
    # before stringify the packet, must assign the labels that marked as 'None'
    b.datapath_id = 00000001
    b.capabilities = 123
    b.actions = 1
    b.n_buffers = 32
    b.show()
    c = str(b)
    print len(c)
    c = c + "AAAAAAAAAAAAAAAAAAAAAAA"
    d = ofp_header(c)
    d.show()
    print len(c)
    
    #if using part of received data, length can be devide by 8 is a must
    d = ofp_features_reply(c[0:39])
    d.show()
    
    #loading scapy packet
    print "-----------------"
    Ether().show()
