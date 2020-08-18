#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse

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
        return self.sprintf("pid=%pid%, UID=%UID%")

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
    parser.add_argument('--UID', type=int, default=None, help='The service UID to use, if unspecified then Tunnel header will not be included in packet')
    parser.add_argument('--tunnel_id', type=int, default=None, help='Tunnel ID that we will use to route packets')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    UID = args.UID
    tunnel_id = args.tunnel_id
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


if __name__ == '__main__':
    main()
