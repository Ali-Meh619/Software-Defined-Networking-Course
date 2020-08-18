# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info


net=Mininet()

c0=net.addController();

h1=net.addHost('h1',ip='10.0.0.1')
h2=net.addHost('h2',ip='10.0.0.6')

s1=net.addSwitch('s1')
s2=net.addSwitch('s2')


net.addLink(h1,s1)
net.addLink(s1,s2)
net.addLink(s2,h2)



info('**** starting network ****')

net.start()

CLI(net)

net.stop()
