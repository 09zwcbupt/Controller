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

Archticture
-----------

