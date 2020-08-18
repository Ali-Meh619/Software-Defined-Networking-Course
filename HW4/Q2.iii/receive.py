#!/usr/bin/env python
"""
We implemented this file similar to the next part, when a hello message is received,
a uid_list.txt file is updated acordingly to keep the UIDs.
afterward an answer message is sent, containing the ip and the Hash value (the UID).
IP packets are handled like before.
"""
import sys
import struct
import os
import json
import re
import time

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
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
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def handle_pkt(pkt):
    if (TCP in pkt and pkt[TCP].dport == 1234):
        print "got a packet"
        pkt.show2()
        pl = bytes(pkt[TCP].payload)
        pl = str(pl)
        matcher1 = re.match(r'hello message, (?P<sender_IP>.*)', pl)
        matcher2 = re.match(r'answer message, (?P<hash>.*) (?P<sender_IP>.*)', pl)
        if matcher1 is not None:
            sender_IP = matcher1.group('sender_IP')
            print("sender_IP : " + sender_IP)
            uid = hash(sender_IP) & 0xFFFF
            saveUID(uid=uid, ip=sender_IP)
            response(sender_IP=sender_IP, uid=uid)
        elif matcher2 is not None:
            uid = matcher2.group('hash')
            ip = matcher2.group('sender_IP')
            setUID(ip=ip, uid=uid)
    if Tunnel in pkt:
        print "got a packet"
        pkt.show2()
        if (TCP in pkt and pkt[TCP].dport == 1234):
            pl = bytes(pkt[TCP].payload)
            pl = str(pl)
            matcher1 = re.match(r'hello message, (?P<sender_IP>.*)', pl)
            matcher2 = re.match(r'answer message, (?P<hash>.*) (?P<sender_IP>.*)', pl)
            if matcher1 is not None:
                sender_IP = matcher1.group('sender_IP')
                print("sender_IP : " + sender_IP)
                uid = hash(sender_IP) & 0xFFFF
                saveUID(uid=uid, ip=sender_IP)
                response(sender_IP=sender_IP, uid=uid)
            elif matcher2 is not None:
                uid = matcher2.group('hash')
                ip = matcher2.group('sender_IP')
                setUID(ip=ip, uid=uid)

        sys.stdout.flush()

def response(sender_IP, uid):
    time.sleep(1)
    os.system('python send.py ' + sender_IP + ' \"answer message, ' + str(uid) + ' ' + sender_IP + '\"')

def saveUID(uid, ip):
    if not os.path.isfile('uid_list.txt'):
        s = str(uid) + '\n'
        uid_file = open('uid_list.txt', 'w')
        uid_file.write(ip + ' : ' + str(uid) + '\n')
        uid_file.close()
    else:
        uid_file = open('uid_list.txt', 'r')
        ls = uid_file.read()
        uid_file.close()
        ls_list = ls.split('\n')
        for element in ls_list:
            if element == (ip + ' : ' + str(uid)):
                return
        ls = ls + ip + ' : ' + str(uid) + '\n'
        uid_file = open('uid_list.txt', 'w')
        uid_file.write(ls)
        uid_file.close()

def setUID(uid, ip):
    uid_file = open(ip+'.txt', 'w')
    uid_file.write(str(uid))
    uid_file.close()

def main():
    bind_layers(Ether, Tunnel, type=TYPE_TUNNEL)
    bind_layers(Tunnel, IP, pid=TYPE_IPV4)
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(count = 1, iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()

