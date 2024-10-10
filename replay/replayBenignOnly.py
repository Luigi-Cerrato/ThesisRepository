import os
import logging
from datetime import datetime, timedelta
from scapy.all import *
import threading

# Definition of the PCAP files
PCAP_BENIGN = "Ton_File_Completed.pcap"

# Log configuration
LOG_FILE = "/replayPackets.log"
MTU_SIZE = 1400  # MTU of your interface

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s: %(message)s')
logging.info("Starting replay_pcap.py script")

# Function to send packets with fragmentation if needed
def send_packet(packet):
    try:
        if len(packet) > MTU_SIZE:
            fragments = fragment(packet, fragsize=MTU_SIZE)
            for frag in fragments:
                sendp(frag, iface="eth0", verbose=False)
                logging.info(f"Sent fragment of size {len(frag)} bytes.")
        else:
            sendp(packet, iface="eth0", verbose=False)
            logging.info(f"Sent packet of size {len(packet)} bytes.")
    except Exception as e:
        logging.error(f"Failed to send packet: {e}")

# Function to handle parallel replay using manual threading
def replay_pcap_parallel(file, duration, label, start_index=0, batch_size=100):
    packets_sent = 0
    if os.path.exists(file):
        logging.info(f"PCAP file found: {file}")
        logging.info(f"Replaying {label} pcap file: {file} for {duration} seconds from packet index {start_index}.")
        
        end_time = datetime.now() + timedelta(seconds=duration)
        threads = []
        try:
            reader = PcapReader(file)
            for idx, packet in enumerate(reader):
                if idx < start_index:
                    continue
                if datetime.now() >= end_time:
                    reader.close()
                    logging.info("Reached end time.")
                    # Wait for all threads to finish before exiting
                    for thread in threads:
                        thread.join()
                    logging.info(f"Packets sent in this session: {packets_sent}")
                    return idx, packets_sent
                logging.debug(f"Processing packet index {idx} of size {len(packet)} bytes.")
                thread = threading.Thread(target=send_packet, args=(packet,))
                thread.start()
                threads.append(thread)
                packets_sent += 1
                if len(threads) >= batch_size:
                    for thread in threads:
                        thread.join()
                    threads = []
            # Wait for remaining threads to finish
            for thread in threads:
                thread.join()
        except Exception as e:
            logging.error(f"Failed to process pcap file: {e}")
    else:
        logging.error(f"PCAP file not found: {file}")
    logging.info(f"Packets sent in this session: {packets_sent}")
    return start_index + packets_sent, packets_sent

# Replay sequence
total_packets_sent = 0
try:
    duration_benign = 600  # Duration in seconds for benign segments

    # Replay 10 minutes of benign traffic
    start_index, packets_sent = replay_pcap_parallel(PCAP_BENIGN, duration_benign, "benign")
    total_packets_sent += packets_sent

except Exception as e:
    logging.error(f"Error during packet replay sequence: {e}")

logging.info(f"Finished replay_pcap.py script, total packets sent: {total_packets_sent}")
print(f"Total packets sent: {total_packets_sent}")
