
from scapy.all import *
import sys, os

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


bind_layers(Ether, Tunnel, type=TYPE_TUNNEL)
bind_layers(Tunnel, IP, pid=TYPE_IPV4)

