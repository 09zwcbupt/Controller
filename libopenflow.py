import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')
from scapy.all import *

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
                  XByteField("pad", 0),
                  XByteField("pad", 0),
                  XByteField("pad", 0),
                  #features
                  BitFieldLenField('capabilities', None, 32, length_of='varfield'),
                  BitFieldLenField('actions', None, 32, length_of='varfield'),
                  #port info can be resoved at TCP server
                ]

bind_layers( ofp_header, ofp_features_reply, type=6 )

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
