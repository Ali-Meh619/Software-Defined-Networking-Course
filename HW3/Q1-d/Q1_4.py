from mininet.net import Mininet
from mininet.node import (RemoteController, 
OVSKernelSwitch)
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from functools import partial
import requests
from requests.auth import HTTPBasicAuth
import time

"""
This code can be executed both with and without a controller (for testing purposes)
If necessary, you may change every defined value as needed.
"""

H1_IP = '10.0.0.1/24'
H1_MAC = '00:00:00:00:00:01'
H2_IP = '20.0.0.1/24'
H2_MAC = '00:00:00:00:00:02'
H1_GW_IP = '10.0.0.254'
H2_GW_IP = '20.0.0.254'
CONTROLLER_IP = '192.168.0.1'
CONTROLLER_PORT = '6653'
H1_IP_nomaks = '10.0.0.1/32'
H2_IP_nomask = '20.0.0.1/32'

def l2MatchingFlow(table_id, flow_id, nw_src, nw_dst, dl_dst, out_port):
    xml = """
    <flow>
        <id>{}</id>
        <cookie_mask>0</cookie_mask>
        <priority>32768</priority>
        <table_id>{}</table_id>
        <match>
            <ipv4-source>{}</ipv4-source>
            <ipv4-destination>{}</ipv4-destination>
            <ethernet-match>
                <ethernet-type>
                    <type>2048</type>
                </ethernet-type>
            </ethernet-match>
        </match>
        <idle-timeout>0</idle-timeout>
        <cookie>0</cookie>
        <flags></flags>
        <hard-timeout>0</hard-timeout>
        <instructions>
            <instruction>
                <order>0</order>
                <apply-actions>
                    <action>
                        <order>1</order>
                        <output-action>
                            <output-node-connector>{}</output-node-connector>
                            <max-length>0</max-length>
                        </output-action>
                    </action>
                    <action>
                        <order>0</order>
                        <set-field>
                            <ethernet-match>
                                <ethernet-destination>
                                    <address>{}</address>
                                </ethernet-destination>
                            </ethernet-match>
                        </set-field>
                    </action>
                </apply-actions>
            </instruction>
        </instructions>
    </flow>
    """.format(flow_id, table_id, nw_src, nw_dst, out_port, dl_dst)

    return xml

def relayFlow(table_id, flow_id, in_port, out_port):
     
    xml = """<flow>
        <id>{}</id>
        <cookie_mask>0</cookie_mask>
        <priority>32768</priority>
        <table_id>{}</table_id>
        <match>
            <in-port>{}</in-port>
            <ethernet-match>
                <ethernet-type>
                    <type>2048</type>
                </ethernet-type>
            </ethernet-match>
        </match>
        <idle-timeout>0</idle-timeout>
        <cookie>0</cookie>
        <flags></flags>
        <hard-timeout>0</hard-timeout>
        <instructions>
            <instruction>
                <order>0</order>
                <apply-actions>
                    <action>
                        <order>0</order>
                        <output-action>
                            <output-node-connector>{}</output-node-connector>
                            <max-length>0</max-length>
                        </output-action>
                    </action>
                </apply-actions>
            </instruction>
        </instructions>
    </flow>""".format(flow_id, table_id, in_port, out_port)

    return xml

def makeTables(switch_id, table_id, flows):
    s1 = ''
    for flow in flows:
        s1 = s1 + flow
    s2 = """ 
    <table xmlns="urn:opendaylight:flow:inventory">
        <id>{}</id>
        {}
    </table>
    """.format(table_id, s1)
    url = 'http://'+CONTROLLER_IP+':'+CONTROLLER_PORT+'/restconf/config/opendaylight-inventory:nodes/node/openflow:{}/table/{}/'.format(
        switch_id,
        table_id
    )
    return (s2, url)

def sendTables(table_list):
    for element in table_list:
        url = element[1]
        xml = element[0]

        headers = {
            'Content-Type' : 'application/xml',
            'Accept' : 'application/xml'
        }
        print requests.put(
            url=url,
            data=xml,
            headers=headers,
            auth=HTTPBasicAuth('admin', 'admin')
        )
    

def Q1_4():
    switch13 = partial(OVSKernelSwitch, protocols='OpenFlow13')

    n = 4
    start = 1
    destination = 4
    graph = [
        [0, 2, 3, 4],
        [2, 0, 0, 1],
        [3, 0, 0, 0],
        [1, 1, 0, 0]
    ]

    visited = list()

    intface_counter = [1 for _ in range(n)]
    edges = dict()

    for i in range(n):
        emp = []
        for j in range(n):
            emp.append(0)
        visited.append(emp)

    p1 = [1, 2, 4]
    p2 = [1, 4]
    
    net = Mininet(
        switch = switch13,
        link = TCLink,
        controller=RemoteController
    )

    h1 = net.addHost(
        'h1',
        ip = H1_IP,
        mac = H1_MAC
    )
    h2 = net.addHost(
        'h2',
        ip = H2_IP,
        mac = H2_MAC
    )

    c0 = net.addController(
        'c0',
        ip=CONTROLLER_IP,
        port=CONTROLLER_PORT
    )

    switch_list = []
    
    for i in range(n):
        name = 's' + str(i + 1)
        s = net.addSwitch(name)
        switch_list.append(s)

    net.addLink(h1, switch_list[start-1])
    edges[('h1', switch_list[start-1].name)] = ('0', '1')
    edges[(switch_list[start-1].name, 'h1')] = ('1', '0')
    intface_counter[start-1] = 2
    net.addLink(h2, switch_list[destination-1])
    edges[('h2', switch_list[destination-1].name)] = ('0', '1')
    edges[(switch_list[destination-1].name, 'h2')] = ('1', '0')
    intface_counter[destination-1] = 2

    for i in range(n):
        for j in range(n):
            if graph[i][j] != 0:
                if visited[i][j] == 0:
                    visited[i][j] = 1
                    visited[j][i] = 1
                    name_i = switch_list[i].name
                    name_j = switch_list[j].name
                    net.addLink(switch_list[i], switch_list[j])
                    edges[(name_i, name_j)] = (intface_counter[i], intface_counter[j])
                    edges[(name_j, name_i)] = (intface_counter[j], intface_counter[i])
                    intface_counter[i] = intface_counter[i] + 1
                    intface_counter[j] = intface_counter[j] + 1
    
    net.build()
    c0.start()
    
    for s in switch_list:
        s.start([c0])

    print('Flows will be added in the next 10 seconds, please reload the controller')
    time.sleep(10)

    print h1.cmd('route add default gw {} h1-eth0'.format(H1_GW_IP))
    print h2.cmd('route add default gw {} h2-eth0'.format(H2_GW_IP))

    print h1.cmd('arp -s {} 00:00:00:00:11:11'.format(H1_GW_IP))
    print h2.cmd('arp -s {} 00:00:00:00:11:11'.format(H2_GW_IP))

    flow_list = [[] for _ in range(n)]
    flow_id_counter = [1 for _ in range(n)]

    # start_name = switch_list[start-1].name
    # destination_name = switch_list[destination-1].name

    # addflow = 'ovs-ofctl -O OpenFlow13 add-flow '

    # print switch_list[start-1].cmd(addflow + start_name + ' table=0,ip,nw_src=20.0.0.0/24,nw_dst=10.0.0.1,actions=mod_dl_dst='+
    #     '00:00:00:00:00:01,output:1')
    flow_list[start-1].append(l2MatchingFlow(
        table_id=0,
        flow_id=flow_id_counter[start-1],
        nw_src=H2_IP,
        nw_dst=H1_IP_nomaks,
        dl_dst=H1_MAC,
        out_port=1
    ))
    flow_id_counter[start-1] = flow_id_counter[start-1] + 1

    # print switch_list[start-1].cmd(addflow + start_name + ' table=0,ip,in_port=1,actions=output:2')
    flow_list[start-1].append(relayFlow(
        table_id=0,
        flow_id=flow_id_counter[start-1],
        in_port=1,
        out_port=2
    ))
    flow_id_counter[start-1] = flow_id_counter[start-1] + 1

    # print switch_list[destination-1].cmd(addflow + destination_name + ' table=0,ip,nw_src=10.0.0.0/24,nw_dst=20.0.0.1,actions=mod_dl_dst='+
    #     '00:00:00:00:00:02,output:1')
    flow_list[destination-1].append(l2MatchingFlow(
        table_id=0,
        flow_id=flow_id_counter[destination-1],
        nw_src=H1_IP,
        nw_dst=H2_IP_nomask,
        dl_dst=H2_MAC,
        out_port=1
    ))
    flow_id_counter[destination-1] = flow_id_counter[destination-1] + 1

    # print switch_list[destination-1].cmd(addflow + destination_name + ' table=0,ip,in_port=1,actions=output:2')
    flow_list[destination-1].append(relayFlow(
        table_id=0,
        flow_id=flow_id_counter[destination-1],
        in_port=1,
        out_port=2
    ))
    flow_id_counter[destination-1] = flow_id_counter[destination-1] + 1

    # print(edges)
    for i in range(len(p1)-2):
        s_now = switch_list[p1[i+1] - 1]
        s_pre = switch_list[p1[i] - 1]
        s_next = switch_list[p1[i+2] - 1]

        in_port = str(edges[(s_now.name, s_pre.name)][0])
        out_port = str(edges[(s_now.name, s_next.name)][0])

        # print s_now.cmd(addflow + s_now.name + ' table=0,in_port=' + in_port + ',actions=output:' + out_port)
        flow_list[p1[i+1] - 1].append(relayFlow(
            table_id=0,
            flow_id=flow_id_counter[p1[i+1] - 1],
            in_port=in_port,
            out_port=out_port
        ))
        flow_id_counter[p1[i+1] - 1] = flow_id_counter[p1[i+1] - 1] + 1

    for i in range(len(p2)-2):
        s_now = switch_list[p2[i+1] - 1]
        s_pre = switch_list[p2[i] - 1]
        s_next = switch_list[p2[i+2] - 1]

        in_port = str(edges[(s_now.name, s_pre.name)][0])
        out_port = str(edges[(s_now.name, s_next.name)][0])

        # print s_now.cmd(addflow + s_now.name + ' table=0,in_port=' + in_port + ',actions=output:' + out_port)
        flow_list[p2[i+1] - 1].append(relayFlow(
            table_id=0,
            flow_id=flow_id_counter[p2[i+1] - 1],
            in_port=in_port,
            out_port=out_port
        ))
        flow_id_counter[p2[i+1] - 1] = flow_id_counter[p2[i+1] - 1] + 1

    table_list = []
    for i in range(n):
        table_list.append(makeTables(
            switch_id=i,
            table_id=0,
            flows=flow_list[i]
        ))

    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    Q1_4()
    