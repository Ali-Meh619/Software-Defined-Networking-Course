#include <core.p4>
#include <v1model.p4>

/*
    This part concerns the implementation of the dedicated bearer, which means
    we must assume that the default bearers have already been processed and the
    type of service for each user is known (which in turn, means the UID fields
    are known, both by the hosts, and the switches).
    We must assume a value for this field, let us assigne a UID=1 for H1 and UID=2
    for H2.

    Oue tunneling protol will use this value as a tunnel destination and another
    filed to indicate the protocol by which the packet should be processed with, 
    either IPV4 or TUNNEL.
*/

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_TUNNEL = 0x1212;      // Convention for our tunneling protocol

/*
    The way we handle QoS is as follows.
    after the UID is obtained, a 16 bit digit, it is AND'ed with 0xFF
    to obtain an 8 bit number, this number is then assigned to the ipv4
    diffserv field.
*/

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

/********* TUNNEL HEADER ***********/
header tunnel_t {
    bit<16> protocolID;     /*  This field indicates the id for the protocol to be used, either :
                                TYPE_IPV4 for ip or TUNNEL for tunneling protocol */
    bit<16> UID;            /*  This field indicates the type of service, each user is assigned a 
                                different service by this UID and, it has not been stated what kind
                                of service is required or what parameters each service needs, but as
                                per instructions, this field is mandetory. 
                                For part I we assume default bearers have already been delivered, so
                                this field is known ...
                                we will use this field to implement QoS in form of Rate Limiting */
    bit<16> tunnel_id;      /*  This field indicates the tunnel ID, which we shall use to route
                                packets from host to server (or the other way around). */
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    bit<32> meter_tag;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tunnel_t     tunnel;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_TUNNEL : parse_tunnel;
            TYPE_IPV4 : parse_ipv4;
            default : accept;
        }
    }

    state parse_tunnel {
        packet.extract(hdr.tunnel);
        transition select(hdr.tunnel.protocolID) {
            TYPE_IPV4 : parse_ipv4;
            default : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action tunnel_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ipv4.diffserv = (bit<8>)(hdr.tunnel.UID & 0xFF);
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table tunnel_exact {
        key = {
            hdr.tunnel.tunnel_id : exact;
        }

        actions = {
            tunnel_forward;
            drop;
        }
        
        size = 1024;
        default_action = drop();
    }

    apply {
        if (hdr.ipv4.isValid() && !hdr.tunnel.isValid()) {
            ipv4_lpm.apply();
        }
        else if (hdr.tunnel.isValid()) {
            tunnel_exact.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.tunnel);
        packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
