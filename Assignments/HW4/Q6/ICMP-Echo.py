import os
import socket
import time
from scapy.all import IP, ICMP, Raw, sr1, conf

HOST = "10.255.255.1"
COUNT = 10
TIMEOUT = 2
PAYLOAD_SIZE = 512
IFACE = None   # "eth0"


def resolve_host(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as e:
        raise ValueError(f"Cannot resolve host '{host}': {e}")


def ping_once(dst_ip, icmp_id, seq, timeout, payload_size):
    payload = bytes((payload_size // 4) * b"PING")[:payload_size]
    pkt = IP(dst=dst_ip) / ICMP(id=icmp_id, seq=seq) / Raw(load=payload)
    t1 = time.perf_counter()
    reply = sr1(pkt, timeout=timeout, verbose=0)
    t2 = time.perf_counter()

    if reply is None:
        return None, None

    rtt_ms = (t2 - t1) * 1000.0
    return reply, rtt_ms


if IFACE:
    conf.iface = IFACE

try:
    dst_ip = resolve_host(HOST)
except ValueError as e:
    print(e)

print(f"PING {HOST} with {PAYLOAD_SIZE} bytes of data:")

icmp_id = os.getpid() & 0xFFFF
sent = 0
received = 0
rtts = []

for seq in range(1, COUNT + 1):
    sent += 1
    reply, rtt_ms = ping_once(dst_ip, icmp_id, seq, TIMEOUT, PAYLOAD_SIZE)

    if reply is not None and reply.haslayer(ICMP) and reply[ICMP].type == 0:
        received += 1
        rtts.append(rtt_ms)
        print(f"{len(reply[Raw].load) if reply.haslayer(Raw) else 0} bytes from {reply.src}: "
              f"icmp_seq={seq} ttl={reply.ttl} time={rtt_ms:.2f} ms")
    else:
        print(f"Request timeout for icmp_seq {seq}")

    time.sleep(1)

print("\n--- {} ping statistics ---".format(HOST))
loss = (sent - received) / sent * 100.0
print(f"{sent} packets transmitted, {received} received, {loss:.1f}% packet loss")

if rtts:
    import statistics
    print(
        f"rtt-->    min:{min(rtts):.2f}ms   |   avg:{statistics.mean(rtts):.2f}ms   |   max:{max(rtts):.2f}ms")
