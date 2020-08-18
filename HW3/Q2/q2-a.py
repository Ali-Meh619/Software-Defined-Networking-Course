#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 18:29:48 2020

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

 

def topology():

        net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )

 

        # Add hosts and switches

        h1 = net.addHost( 'green2', ip="10.0.0.2/24", mac="00:00:00:00:00:02" )

        h2 = net.addHost( 'blue2', ip="10.0.0.2/24", mac="00:00:00:00:00:02" )

        

        s1 = net.addSwitch( 's1')

        

        #c0 = net.addController(  )

 

        

        net.addLink( h1, s1 )

        net.addLink( h2, s1 )

        net.build()

        #c0.start()

        s1.start([])

        

 

        print ("*** Running CLI")

        CLI( net )

 

        print ("*** Stopping network")

        net.stop()

      

if __name__ == '__main__':

    setLogLevel( 'info' )

    topology()  
