import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')
from scapy.all import *

#uint8_t => XByteField
#uint16_t => ShortField, BitFieldLenField('name', None, 16, length_of='varfield')
#uint32_t => IntField, BitFieldLenField('name', None, 32, length_of='varfield'),

###################
# Data Structures #
###################

class ofp_phy_port(Packet):
    name = "OpenFlow Port"
    fields_desc=[ ShortField("port_no", 0),
                  MACField("hw_addr", 0),
                  StrField("port_name", None, fmt="H", remain=24),

                  #TODO: still some problem with this part
                  #uint32_t for port config, for Openflow 1.0, this part only uses 7 bits.
                  BitField("OFPPC_PORT_DOWN", None, 1),
                  BitField("OFPPC_NO_STP", 0, 1),
                  BitField("OFPPC_NO_RECV", 0, 1),
                  BitField("OFPPC_NO_RECV_STP",0, 1),
                  BitField("OFPPC_NO_FLOOD", 0, 1),
                  BitField("OFPPC_NO_FWD", 0, 1),
                  BitField("OFPPC_NO_PACKET_IN", 0, 1),
                  BitField("config not defined", 0, 25),

                  #uint32_t for state
                  BitField("OFPPS_LINK_DOWN", 0, 1),
                  BitField("else", 0, 31),

                  #uint32_t for Current features
                  BitField("OFPPF_10MB_HD", 0, 1),
                  BitField("OFPPF_10MB_FD", 0, 1),
                  BitField("OFPPF_100MB_HD", 0, 1),
                  BitField("OFPPF_100MB_FD", 0, 1),
                  BitField("OFPPF_1GB_HD", 0, 1),
                  BitField("OFPPF_1GB_FD", 0, 1),
                  BitField("OFPPF_10GB_FD", 0, 1),
                  BitField("OFPPF_COPPER", 0, 1),
                  BitField("OFPPF_FIBER", 0, 1),
                  BitField("OFPPF_AUTONEG", 0, 1),
                  BitField("OFPPF_PAUSE", 0, 1),
                  BitField("OFPPF_PAUSE_ASYM", 0, 1),
                  BitField("curr_not defined", 0, 20),

                  #uint32_t for features being advised by the port
                  BitField("advertised", 0, 32),

                  #uint32_t for features supported by the port
                  BitField("supported", 0, 32),
 
                  #uint32_t for features advertised by peer
                  BitField("peer", 0, 32)
                ]

###################
# OpenFlow Header #
###################

class ofp_header(Packet):
    name = "OpenFlow Header "
    fields_desc=[ XByteField("version",1),
                 ByteEnumField("type",0,
                     {
                         0: "OFPT_HELLO",
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
                         21: "OFPT_QUEUE_GET_CONFIG_REPLY",
                         #Messages for circuit switched ports
                         #255: "OFPT_CFLOW_MOD",
                     }),
                 ShortField("length",8),
                 IntField("xid" , 1) ]

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

# No. 10
class ofp_packet_in(Packet):
    name = "OpenFlow Packet In"
    fields_desc=[ IntField("buffer_id", None),
                  ShortField("total_len", None),
                  ShortField("in_port", None),
                  ByteEnumField("reason", 0,
                      {
                         0: "OFPR_NO_MATCH",
                         1: "OFPR_ACTION",
                      }),
                  ByteField("pad", None)
                ]

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
