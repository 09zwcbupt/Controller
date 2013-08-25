Architecture
============

This part talks about the archticture of this OpenFlow Controller.
As OpenFlow switches are able to establish connections with OpenFlow controller using TCP protocol, accroding to OpenFlow Switch Specification, the bottom part of a controller should be a layer containing TCP connection handler. So, in our design, we use a TCP server to handle connections from OpenFlow switches. When OpenFlow switch tries to make a connection, the TCP server handles its request and return a stable TCP connection. After that, the communication between controller and switch would be formatted according to the OpenFlow protocol.
In order to pack and parse messages in OpenFlow protocol, the controller needs a library beyond the bottom layer. For us, we use Scapy and worte a simple library for this work. Once received a message from OpenFlow switch, the controller first tries to judge the message to be an OpenFlow message by measuring its length. 
