/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


/* Value Definitions */
#define NUM_STAGES 4      
#define STAGE_CAPACITY 16   
#define WEIGHT_WIDTH 16     
#define PORT_WIDTH 15      
#define MAX_HOPS 5        
/*------- ToDo: here you can write your value definitions -------*/


/* Constant values */
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> BALLAANCED = 0x4231;      
const bit<16> TYPE_DASH = 0x4567;    

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

/* Type Definition */
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<WEIGHT_WIDTH> weight_t;
typedef bit<WEIGHT_WIDTH> boundary_t;
typedef bit<PORT_WIDTH> port_t;
typedef bit<9> egressSpec_t;
/*------- ToDo: here you can write your type definitions -------*/


/* Headers */
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
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

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

header dash_t {
    weight_t weight;
}

header srcRoute_t {
    bit<1>    bos;
    port_t   port;
}

struct metadata {
    /*------- ToDo: here you can define your metadata -------*/
    bit<16>  hash;
    bit<1>   balanced;
    bit<1>   final;
}

struct headers {
    ethernet_t              ethernet;
    srcRoute_t[MAX_HOPS]    srcRoutes;
    ipv4_t                  ipv4;
    udp_t                   udp;
    dash_t                  dash;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

/* Keep this unchanged */

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
            TYPE_DASH : parse_dash;
            TYPE_IPV4 : parse_ipv4;
            BALLAANCED : parse_ipv4;
            default   : accept;
        }
    }

    state parse_dash {
        packet.extract(hdr.dash);
        transition parse_srcRouting;
    }

    state parse_srcRouting {
        packet.extract(hdr.srcRoutes.next);
        transition select(hdr.srcRoutes.last.bos) {
            1       : parse_ipv4;
            default : parse_srcRouting;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w17: parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

/* Keep this unchanged */

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    
    register<boundary_t>(STAGE_CAPACITY*4) boundary_reg;


   action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    /*------- ToDo: here you can define your actions and tables -------*/

    /* pop an entery from the port list and set it as egress_spec */
    action srcRoute_nhop() {
        standard_metadata.egress_spec = (bit<9>)hdr.srcRoutes[0].port;
        hdr.srcRoutes.pop_front(1);
    }

    /* set etherType when bottom of stack is reached */
    action srcRoute_finish() {
        hdr.ethernet.etherType = TYPE_IPV4;
        //boundary_reg.write(((bit<32>)(standard_metadata.ingress_port) - (bit<9>)2), hdr.dash.weight);
    }

    /* relay packets for s3, s4, s5 and s6 */
    action relay() {
        if (standard_metadata.ingress_port == (bit<9>)1) {
            standard_metadata.egress_spec = (bit<9>)2;
        } 
        else if (standard_metadata.ingress_port == (bit<9>)2) {
            standard_metadata.egress_spec = (bit<9>)1;
        }
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

    apply {
        
        // handle DASH packets.
        if (hdr.dash.isValid()){            
            
            if (hdr.srcRoutes[0].isValid()){
                if (hdr.srcRoutes[0].bos == 1){
                    srcRoute_finish();

                    if (standard_metadata.ingress_port == 2){
                        boundary_reg.write((bit<32>)0,hdr.dash.weight);
                    }
                    else if (standard_metadata.ingress_port == 3){
                        boundary_reg.write((bit<32>)1,hdr.dash.weight);
                    }
                    else if (standard_metadata.ingress_port == 4){
                        boundary_reg.write((bit<32>)2,hdr.dash.weight) ;
                    }
                    else if (standard_metadata.ingress_port == 5){
                        boundary_reg.write((bit<32>)3,hdr.dash.weight) ;
                    }
                }
                srcRoute_nhop();
            }
            else {
                drop();
            }
        }
        // for UDP packets.
        else if (hdr.ipv4.isValid()) {
            /*------- ToDo: here you can define your control flow for ordinary Data probe packets -------*/

            /* use this Hash function: */
            hash(
            meta.hash,
            HashAlgorithm.crc16,
            (bit<16>)0,
            {hdr.ipv4.srcAddr, hdr.ipv4.dstAddr},
            (bit<16>)30);

            bit<16> b1;
            bit<16> b2;
            bit<16> b3;
            bit<16> b4;

            boundary_reg.read(b1,0);
            boundary_reg.read(b2,1);
            boundary_reg.read(b3,2);
            boundary_reg.read(b4,3);

            if (hdr.ethernet.etherType == 0x800){
                hdr.ethernet.etherType = BALLAANCED; //the packet is now ballanced
                if ((bit<16>)meta.hash < b1){
                    standard_metadata.egress_spec = (bit<9>)2;/*
                    hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
                    hdr.ethernet.dstAddr = 0x000000030300;
                    hdr.ipv4.ttl = hdr.ipv4.ttl - 1;*/
                }
                else {
                    if ((bit<16>)meta.hash < b2) {
                        standard_metadata.egress_spec = (bit<9>)3;/*
                        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
                        hdr.ethernet.dstAddr = 0x000000040400;
                        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;*/
                    }
                    else {
                        if ((bit<16>)meta.hash < b3) {
                            standard_metadata.egress_spec = (bit<9>)4;/*
                            hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
                            hdr.ethernet.dstAddr = 0x000000050500;
                            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;*/
                        }
                        else {
                            standard_metadata.egress_spec = (bit<9>)5;/*
                            hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
                            hdr.ethernet.dstAddr = 0x000000060600;
                            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;*/
                        }
                    }
                }
            }
            else if (hdr.ethernet.etherType == BALLAANCED) {
                relay();
            }
	    else {
	    	ipv4_lpm.apply();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

/* Keep this unchanged */

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

/* Keep this unchanged */

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
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

/* Keep this unchanged */

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.dash);
        packet.emit(hdr.srcRoutes);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

/* Keep this unchanged */

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;