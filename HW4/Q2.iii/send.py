#!/usr/bin/env python
"""
We implemented this part like what we shall do in part 3.
IP packets are sent normally, unless they are hello messages, which
causes the program to run a receive.py script to handle the answer
response, after that, a text file with the name of the host ip will
be created, containing the host's UID.

Afterward, if a tunnel packet (a dedicated bearer) needs to be sent,
the program will read the UID from the created file instead of getting
it from the user.
QoS functionality is also done the same way as before.
"""
import argparse
import sys
import os
import socket
import random
import struct
import argparse
import re

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import ShortField, bind_layers
# from tunnel_header import Tunnel

TYPE_TUNNEL = 0x1212
TYPE_IPV4 = 0x0800

class Tunnel(Packet):
    name = "Tunnel"
    fields_desc = [
        ShortField("pid", 0),
        ShortField("UID", 0),
        ShortField("tunnel_id", 0)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, UID=%UID%, tunnel_id=%tunnel_id%")

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():
    bind_layers(Ether, Tunnel, type=TYPE_TUNNEL)
    bind_layers(Tunnel, IP, pid=TYPE_IPV4)

    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('dedicated', type=str, default=None, help="Does this packet contain a dedicated bearer?")
    # parser.add_argument('--UID', type=int, default=None, help='The service UID to use, if unspecified then Tunnel header will not be included in packet')
    #parser.add_argument('--tunnel_id', type=int, default=None, help='Tunnel ID that we will use to route packets')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    # UID = args.UID
    matcher = re.match(r'hello message, (.*)', args.message)

    if os.path.isfile(args.ip_addr + '.txt') and matcher is None and args.dedicated is not None:
        uid_file = open(args.ip_addr + '.txt', 'r')
        UID = int(uid_file.read()) & 0xFFFF
        tunnel_id = UID
    else:
        UID = None
        tunnel_id = None
    # tunnel_id = args.tunnel_id
    iface = get_if()

    if (UID is not None and tunnel_id is not None):
        print "sending on interface {} to UID {} and tunnel_id {}".format(iface, str(UID), str(tunnel_id))
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / Tunnel(UID=UID, tunnel_id=tunnel_id) / IP(dst=addr) / args.message
    else:
        print "sending on interface {} to IP addr {}".format(iface, str(addr))
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / args.message

    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)

    if matcher is not None:
        os.system('python receive.py')


if __name__ == '__main__':
    main()
