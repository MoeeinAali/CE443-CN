from scapy.all import IP, ICMP, sr1

def send_ttl_expired(dst_ip):
    pkt = IP(dst=dst_ip, ttl=1) / ICMP()
    reply = sr1(pkt, timeout=2, verbose=1)
    
    if reply:
        reply.show()  
    else:
        print("No reply received")

if __name__ == "__main__":
    send_ttl_expired("8.8.8.8")
