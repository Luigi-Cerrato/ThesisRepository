import dpkt
import socket

# Open the pcap file for reading
with open('inputFile.pcap', 'rb') as f:
    pcap = dpkt.pcap.Reader(f)

    # Create new pcap writers for benign and malicious packets
    benign_pcap = dpkt.pcap.Writer(open('benign.pcap', 'wb'))
    malicious_pcap = dpkt.pcap.Writer(open('malicious.pcap', 'wb'))

    # Process each packet in the input pcap
    for timestamp, buf in pcap:
        try:
            # Decode the Ethernet packet
            eth = dpkt.ethernet.Ethernet(buf)

            # Check for VLAN, skip if present
            if eth.type == 0x8100:  # VLAN tag type
                eth = dpkt.ethernet.Ethernet(eth.data)

            # Skip non-IPv4 packets
            if not isinstance(eth.data, dpkt.ip.IP):
                continue

            ip = eth.data

            # Extract IP addresses
            ip_src = socket.inet_ntoa(ip.src)
            ip_dst = socket.inet_ntoa(ip.dst)

            # Initialize port numbers
            src_port = dst_port = 0
            label = 0  # 0 for benign, 1 for malicious

            # Check if it's a TCP or UDP packet
            if isinstance(ip.data, dpkt.tcp.TCP):
                tcp = ip.data
                src_port = tcp.sport
                dst_port = tcp.dport
            elif isinstance(ip.data, dpkt.udp.UDP):
                udp = ip.data
                src_port = udp.sport
                dst_port = udp.dport

            # Check if the packet is malicious (port 9)
            if src_port == 9 or dst_port == 9:
                label = 1

            # Write to the appropriate pcap file based on the label
            if label == 1:
                malicious_pcap.writepkt(buf, ts=timestamp)
            else:
                benign_pcap.writepkt(buf, ts=timestamp)

        except Exception as e:
            print(f"Error processing packet at timestamp {timestamp}: {e}")
            continue

    # Close the pcap writers
    benign_pcap.close()
    malicious_pcap.close()

print("PCAP processing complete. Saved benign and malicious packets.")
