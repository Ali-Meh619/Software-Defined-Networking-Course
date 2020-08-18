#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 12:17:31 2020

@author: mininet
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 12:11:54 2020

@author: mininet
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 09:07:51 2020

@author: mininet
"""

from mininet.net import Mininet

from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch

from mininet.cli import CLI

from mininet.log import setLogLevel

from mininet.link import Link, TCLink

from functools import partial


 

def topology():
    
    
    
        sswitch=partial(OVSKernelSwitch,protocols='OpenFlow13')
        net = Mininet( controller=RemoteController, link=TCLink, switch=sswitch )

 

        # Add hosts and switches

        h30 = net.addHost( 'h30', ip="10.0.0.1/24", mac="00:00:00:00:00:01" )

        h40 = net.addHost( 'h40', ip="20.0.0.1/24", mac="00:00:00:00:00:02" )

        s33 = net.addSwitch( 's33')

        s11 = net.addSwitch( 's11')

        s22 = net.addSwitch( 's22')

        c0 = net.addController( 'c0', controller=RemoteController, ip='192.168.1.156', port=6653 )

 
        net.addLink( h30, s11 )
        net.addLink( s33, s11 )
        net.addLink( s33, s22 )
        net.addLink( h40, s22 )


        net.build()
        c0.start()

        s11.start( [c0] )
        s22.start( [c0] )
        s33.start( [c0] )

        h30.cmd("route add default gw 10.0.0.254 h30-eth0")
        h30.cmd("arp -s 10.0.0.10 00:00:00:00:11:11")

        h40.cmd("route add default gw 20.0.0.254 h40-eth0")
        h40.cmd("arp -s 20.0.0.10 00:00:00:00:11:11")

        

 

        print ("*** Running CLI")

        CLI( net )

 

        print ("*** Stopping network")

        net.stop()

      

if __name__ == '__main__':

    setLogLevel( 'info' )

    topology()  
