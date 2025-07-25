import os
import socket
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11

def checksum(data: bytes) -> int:
    s = 0
    n = len(data)
    count = 0

    while count + 1 < n:
        s += (data[count] << 8) + data[count + 1]
        s &= 0xffffffff
        count += 2

    if n & 1:
        s += data[-1] << 8
        s &= 0xffffffff

    s = (s >> 16) + (s & 0xffff)
    s += (s >> 16)
    return (~s) & 0xffff

def create_packet(ident: int, seq: int = 1) -> bytes:
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, ident, seq)
    data = struct.pack('!d', time.time())
    chksum = checksum(header + data)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, chksum, ident, seq)
    return header + data

def set_ttl(sock: socket.socket, ttl: int):
    level = socket.IPPROTO_IP
    optname = socket.IP_TTL

    try:
        sock.setsockopt(level, optname, ttl)
    except OSError:
        sock.setsockopt(level, optname, struct.pack('I', ttl))

def traceroute(dest_name: str, max_hops: int = 30, timeout: float = 2.0):
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print(f"Unknown host: {dest_name}")
        return

    print(f"Traceroute to {dest_name} ({dest_addr}), max hops: {max_hops}")

    for ttl in range(1, max_hops + 1):
        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            print("PermissionError")
            return

        set_ttl(send_socket, ttl)
        recv_socket.settimeout(timeout)
        recv_socket.bind(("", 0))

        packet_id = (os.getpid() & 0xFFFF) ^ ttl
        packet = create_packet(packet_id)

        send_time = time.time()
        send_socket.sendto(packet, (dest_addr, 0))

        curr_addr = None
        curr_name = None

        try:
            ready = select.select([recv_socket], [], [], timeout)
            if not ready[0]:
                print(f"{ttl:2d}  *")
                continue

            recv_packet, addr = recv_socket.recvfrom(1024)
            recv_time = time.time()
            curr_addr = addr[0]
            rtt = (recv_time - send_time) * 1000.0

            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr

            icmp_header = recv_packet[20:28]
            icmp_type, code, chksum, p_id, seq = struct.unpack("!BBHHH", icmp_header)

            if icmp_type == ICMP_TIME_EXCEEDED:
                print(f"{ttl:2d}  {curr_name} ({curr_addr})  {rtt:.3f} ms")
            elif icmp_type == ICMP_ECHO_REPLY:
                print(f"{ttl:2d}  {curr_name} ({curr_addr})  {rtt:.3f} ms")
                print("Reached destination.")
                break
            else:
                print(f"{ttl:2d}  {curr_addr}  (unexpected ICMP type {icmp_type})  {rtt:.3f} ms")

        except socket.timeout:
            print(f"{ttl:2d}  *")
        finally:
            send_socket.close()
            recv_socket.close()

traceroute("sharif.ir")
