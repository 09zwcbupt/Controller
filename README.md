CATR Controller
===============

This is my first OpenFlow controller, wrote for the CATR (for testing).
Also, this is an experimental project for Wang jian, kimi Yang and me. Our goals are:

    · Add ovsdb-management protocol into the controller (like a driver)
    · Make module/app that can be removed on the fly
    · And everything we would come up with

So, instead of performance (not able to do so), we focus on the functionality of a controller.
Below is the structure of this document:

     CATR Controller -+- Architecture -+- Overall  
                      |                |  
                      |                +- Step by step -+- Tornado & Echo Server  
                      |                                 |  
                      |                                 +- Scapy & OpenFlow lib  
                      +- Detailed Design -+- TCP Server  
                      |                   |  
                      |                   +- OpenFlow Library  
                      |                   |  
                      |                   +- Event System  
                      +- Idea List  

Architecture
------------
###Overall
The CATR Controller is first started as a testing tool for the OpenFlow cricuit extension project in CATR of MIIT.  
This is a pic of current architecture:  
![Arch](http://richardzhao.me/wp-content/uploads/2013/08/archi.png)  
It has three layers. The bottom one is the TCP Server, handling TCP connections started from OpenFlow Switches.  
The second one is a Openflow library which will parse upcomming messages and pack message to switches.
And the third layer is processing logic.

###Step by step
As shown in the previous picture. The bottom of CATR Controller is a TCP server using IOLoop in tornado.
