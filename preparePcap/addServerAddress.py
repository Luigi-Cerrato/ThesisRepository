# This script processes ALL packets by replacing the destination IP with 10.0.0.1
# and setting dstport=9 ONLY for malicious files, controlled by the 'benign' flag.
from scapy.all import PcapReader, PcapWriter, IP, TCP, UDP

input_file = 'Ton_IoT_File.pcap'
output_file = 'Ton_File_withAddress.pcap'

# Optional limit of packets to modify
max_packets = None
packet_count = 0

# Flag to indicate if packets are benign (1 = benign, 0 = malicious)
benign = 1  # Set to 0 for malicious files

# Use PcapReader to read packets one at a time
with PcapReader(input_file) as reader, PcapWriter(output_file, sync=True) as writer:
    for packet in reader:
        if IP in packet:
            # Modify the destination IP address
            packet[IP].dst = '10.0.0.1'
            del packet[IP].chksum  # Remove checksum to force recalculation
            
            # Only modify the port if the packet is malicious (benign == 0)
            if benign == 0:
                # Check if the packet has a TCP or UDP transport layer
                if TCP in packet:
                    packet[TCP].dport = 9  # Modify the TCP destination port
                    del packet[TCP].chksum  # Remove checksum to force recalculation
                elif UDP in packet:
                    packet[UDP].dport = 9  # Modify the UDP destination port
                    del packet[UDP].chksum  # Remove checksum to force recalculation
        
        writer.write(packet)
        packet_count += 1
        
        # Check if the packet limit has been reached
        if max_packets is not None and packet_count >= max_packets:
            print(f'Packet limit of {max_packets} reached. Stopping process.')
            break
