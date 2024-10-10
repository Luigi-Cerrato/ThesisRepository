from scapy.all import *

# This script adds TCP and Ethernet headers to all packets that do not have one.
def add_ethernet_udp_header(pcap_file, output_file, packet_limit):
    # Read only the first 'packet_limit' packets from the existing pcap file
    packets = rdpcap(pcap_file, count=packet_limit)

    # List for the modified packets
    modified_packets = []

    # Add an Ethernet and UDP header to the read packets
    for pkt in packets:
        if IP in pkt:
            eth = Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff")
            if UDP not in pkt:
                udp = UDP()
                ip_layer = pkt[IP].copy()
                new_pkt = eth / ip_layer / udp / pkt[IP].payload
            else:
                new_pkt = eth / pkt[IP]
            modified_packets.append(new_pkt)
        else:
            # If the packet does not contain IP, leave it unchanged
            modified_packets.append(pkt)

    # Save the modified packets to a new pcap file
    wrpcap(output_file, modified_packets)

# Execute the function with the input and output pcap files
input_pcap = "Ton_File_withAddress.pcap"
output_pcap = "Ton_File_Completed.pcap"
packet_limit = 1500000
add_ethernet_udp_header(input_pcap, output_pcap, packet_limit)
