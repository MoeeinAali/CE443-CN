import socket
import struct
import os

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5005
BUFFER_SIZE = 4096
DOWNLOAD_DIR = './client_downloaded_files/'
TIMEOUT = 0.5


def calculate_checksum(data):
    return sum(data) % 65535 if data else 1


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

filename = input("Enter filename: ")

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

packet = struct.pack('!BHI', 0, 0, 0) + filename.encode()
sock.sendto(packet, (SERVER_IP, SERVER_PORT))
print(f"[SEND] Sent FILENAME request for '{filename}'")

f = open(os.path.join(DOWNLOAD_DIR, filename), 'wb')

expected_seq = 0

while True:
    try:
        sock.settimeout(5)
        data, _ = sock.recvfrom(BUFFER_SIZE)

    except socket.timeout:
        print("[ERROR] Timeout waiting for server.")
        break

    header = data[:7]
    payload = data[7:]
    packet_type, seq_num, recv_checksum = struct.unpack('!BHI', header)

    if packet_type == 3:
        print("[ERROR] Server reported error:", payload.decode())
        f.close()
        os.remove(os.path.join(DOWNLOAD_DIR, filename))
        break

    if packet_type == 4:
        print("[DONE] File download completed.")
        f.close()
        break

    if packet_type == 1:
        checksum = calculate_checksum(payload)
        print(
            f"[RECV] Received DATA packet Seq={seq_num} Checksum={recv_checksum} (Calculated={checksum})")

        if checksum == recv_checksum and seq_num == expected_seq:
            f.write(payload)

            ack_packet = struct.pack('!BHI', 2, seq_num, 0)
            sock.sendto(ack_packet, (SERVER_IP, SERVER_PORT))
            print(f"[SEND] Sent ACK for Seq={seq_num}")
            expected_seq += 1
        else:
            nack_packet = struct.pack('!BHI', 5, seq_num, 0)
            sock.sendto(nack_packet, (SERVER_IP, SERVER_PORT))
            print(f"[SEND] Sent NACK for Seq={seq_num}")

sock.close()
