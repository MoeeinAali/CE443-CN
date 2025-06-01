import random
import socket

def checksum(chk_data: bytes):
    if len(chk_data) % 2 != 0:
        chk_data += b'\x00'
    total = 0
    for i in range(0, len(chk_data), 2):
        word = (chk_data[i] << 8) | chk_data[i+1]
        total += word
    total = (total & 0xffff) + (total >> 16)
    return (~total & 0xffff).to_bytes(2, byteorder='big')

def simple_ip(id, mf_flag, frag_off, ttl, proto, src_ip, dst_ip, payload):
    ver_ihl = (0x45).to_bytes(1, byteorder='big')
    dscp_ecn = (0x00).to_bytes(1, byteorder='big')
    total_len = (20 + len(payload)).to_bytes(2, byteorder='big')
    identification = id.to_bytes(2, byteorder='big')
    frag_off_val = (frag_off & 0x1fff) | ((mf_flag & 3) << 13)
    frag_off_bytes = frag_off_val.to_bytes(2, byteorder='big')
    ttl_byte = ttl.to_bytes(1, byteorder='big')
    proto_byte = proto.to_bytes(1, byteorder='big')

    chksum = checksum(ver_ihl + dscp_ecn + total_len + identification + frag_off_bytes + ttl_byte + proto_byte + src_ip + dst_ip)
    ip_header = ver_ihl + dscp_ecn + total_len + identification + frag_off_bytes + ttl_byte + proto_byte + chksum + src_ip + dst_ip
    return ip_header + payload

def simple_udp(src_ip, dst_ip, src_port, dst_port, payload):
    src_port_bytes = src_port.to_bytes(2, byteorder='big')
    dst_port_bytes = dst_port.to_bytes(2, byteorder='big')
    udp_len = (8 + len(payload)).to_bytes(2, byteorder='big')
    chksum = (0x0000).to_bytes(2, byteorder='big')
    udp_header = src_port_bytes + dst_port_bytes + udp_len + chksum
    return udp_header + payload

def simple_udp_ip(id, mf_flag, frag_off, ttl, src_ip, dst_ip, src_port, dst_port, payload):
    udp = simple_udp(src_ip, dst_ip, src_port, dst_port, payload)
    return simple_ip(id, mf_flag, frag_off, ttl, socket.IPPROTO_UDP, src_ip, dst_ip, udp)


import socket

class Client:
    def __init__(self, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.src_ip = socket.inet_aton('127.0.0.1')
        self.dst_ip = socket.inet_aton('127.0.0.1')
        self.src_port = random.randint(1024, 65535)
        self.dst_port = server_port

    def send(self, data: bytes, data_frag_len=128, ttl_func=lambda: 64):
        transid = random.randint(1, (1 << 16) - 1)
        dptr = 0
        data = simple_udp(self.src_ip, self.dst_ip, self.src_port, self.dst_port, data)
        while dptr * 8 + data_frag_len < len(data):
            self.send_frag(transid, 0x1, dptr, data[dptr * 8:dptr * 8 + data_frag_len], ttl_func())
            dptr += data_frag_len // 8
        self.send_frag(transid, 0x0, dptr, data[dptr * 8:], ttl_func())

    def send_frag(self, id, mf_flag, frag_off, data: bytes, ttl):
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        self.sock.sendto(
            simple_ip(id, mf_flag, frag_off, ttl, socket.IPPROTO_UDP, self.src_ip, self.dst_ip, data),
            ('127.0.0.1', self.dst_port)
        )

class Server:
    def __init__(self, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', server_port))
        while True:
            dta, addr = self.sock.recvfrom(1024)
            print(dta.decode('ascii'))
