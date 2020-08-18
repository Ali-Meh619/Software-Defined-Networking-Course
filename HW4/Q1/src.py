#!/usr/bin/env python

from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP, TCP
from time import sleep


def get_if():
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface


def main():
    src_ip = "10.0.1.1"
    dst_ip = "10.0.1.2"
    iface = get_if()

    while True:
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=dst_ip, src=src_ip) / UDP(dport=4321, sport=1234)
        sendp(pkt, iface=iface, verbose=False)
        sleep(0.5)


if __name__ == '__main__':
    main()
