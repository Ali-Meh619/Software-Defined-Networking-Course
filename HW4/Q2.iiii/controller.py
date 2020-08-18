#!/usr/bin/env python2
"""
The functionality of this file is very diverse, we will explain
every part in the coments ...
"""
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

# The controller will open uid_list.txt which contains a list
# of ip : uid pairs for each host, and will turn it into a python dict.
uid_file = open('uid_list.txt', 'r')
ls = uid_file.read()
ls_list = ls.split('\n')
ls_list.remove('')
for i in range(len(ls_list)):
    ls_list[i] = ls_list[i].split(' : ')
for i in range(len(ls_list)):
    ls_list[i][1] = int(ls_list[i][1]) & 0xFFFF
print(ls_list)
pair_dict = dict()

for i in range(len(ls_list)):
    pair_dict[ls_list[i][1]] = ls_list[i][0]

def writeTunnelRules(p4info_helper, ingress_sw):
    """
    Installs dedicated bearer tunneling rules.
    """
    for uid in pair_dict.keys():
        ip = pair_dict[uid]
        print(ip)
        print(uid)
        if (ingress_sw.name == 's1'):
            table_entry = p4info_helper.buildTableEntry(
                table_name="MyIngress.tunnel_exact",
                match_fields={
                    "hdr.tunnel.tunnel_id": uid
                },
                action_name="MyIngress.tunnel_forward",
                action_params={
                    "port": 1
                })
            ingress_sw.WriteTableEntry(table_entry)

        elif (ingress_sw.name == 's2'):
            if ip == '10.0.2.2' or ip == '10.0.3.3':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 1
                    })
                ingress_sw.WriteTableEntry(table_entry)
        elif (ingress_sw.name == 's3'):
            if ip == '10.0.5.5' or ip == '10.0.4.4':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 1
                    })
                ingress_sw.WriteTableEntry(table_entry)
        elif (ingress_sw.name == 's4'):
            if ip == '10.0.2.2':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 2
                    })
                ingress_sw.WriteTableEntry(table_entry)
        elif (ingress_sw.name == 's5'):
            if ip == '10.0.3.3':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 2
                    })
                ingress_sw.WriteTableEntry(table_entry)
        elif (ingress_sw.name == 's6'):
            if ip == '10.0.4.4':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 2
                    })
                ingress_sw.WriteTableEntry(table_entry)
        elif (ingress_sw.name == 's7'):
            if ip == '10.0.5.5':
                table_entry = p4info_helper.buildTableEntry(
                    table_name="MyIngress.tunnel_exact",
                    match_fields={
                        "hdr.tunnel.tunnel_id": uid
                    },
                    action_name="MyIngress.tunnel_forward",
                    action_params={
                        "port": 2
                    })
                ingress_sw.WriteTableEntry(table_entry)

def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print "%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            )

def printGrpcError(e):
    """
    Error handeling, mostly for debug ...
    """
    print "gRPC Error:", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    traceback = sys.exc_info()[2]
    print "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create switch objects ...
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s7',
            address='127.0.0.1:50057',
            device_id=6,
            proto_dump_file='logs/s7-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()
        s7.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s1"
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s2"
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s3"
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s4"
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s5"
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s6"
        s7.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s7"


        # Installing flow tables
        writeTunnelRules(p4info_helper, ingress_sw=s1)
        writeTunnelRules(p4info_helper, ingress_sw=s2)
        writeTunnelRules(p4info_helper, ingress_sw=s3)
        writeTunnelRules(p4info_helper, ingress_sw=s4)
        writeTunnelRules(p4info_helper, ingress_sw=s5)
        writeTunnelRules(p4info_helper, ingress_sw=s6)
        writeTunnelRules(p4info_helper, ingress_sw=s7)
        
        while True:
            sleep(5)
            print('****COOUNTER****')
            for uid in pair_dict.keys():
                printCounter(p4info_helper, s1, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s2, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s3, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s4, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s5, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s6, "MyIngress.uid_counter", uid)
                printCounter(p4info_helper, s7, "MyIngress.uid_counter", uid)

    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/problem2_4.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/problem2_4.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
