import socket
import os
import struct
import time
import random

SERVER_IP = '0.0.0.0'
SERVER_PORT = 5005
BUFFER_SIZE = 4096
FILE_DIR = './server_files/'
PACKET_SIZE = 2048
TIMEOUT = 0.5

LOSS_PROBABILITY = 0.2
CORRUPT_PROBABILITY = 0.1
DELAY_PROBABILITY = 0.3
MAX_DELAY = 2


def calculate_checksum(data):
    return sum(data) % 65535 if data else 1


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

while True:
    print("\n[WAIT] Waiting for new file request...")
    sock.settimeout(None)
    data, addr = sock.recvfrom(BUFFER_SIZE)

    header = data[:7]
    payload = data[7:]

    packet_type, seq_num, recv_checksum = struct.unpack('!BHI', header)

    if packet_type == 0:
        filename = payload.decode()
        file_path = os.path.join(FILE_DIR, filename)

        print(f"[REQUEST] Client {addr} requested file: {filename}")

        if not os.path.exists(file_path):
            error_packet = struct.pack('!BHI', 3, 0, 0) + b"File Not Found"
            sock.sendto(error_packet, addr)
            print("[ERROR] File Not Found sent to client.")
            continue

        with open(file_path, 'rb') as f:
            seq = 0
            while True:
                chunk = f.read(PACKET_SIZE)
                if not chunk:
                    break

                original_chunk = chunk

                if random.random() < CORRUPT_PROBABILITY:
                    chunk = bytearray(chunk)
                    if len(chunk) > 0:
                        chunk[0] ^= 0xFF
                    chunk = bytes(chunk)
                    print(
                        f"[CORRUPT] Simulated corruption in packet Seq={seq}")

                checksum = calculate_checksum(chunk)
                packet = struct.pack('!BHI', 1, seq, checksum) + chunk

                while True:
                    if random.random() < LOSS_PROBABILITY:
                        print(f"[DROP] Simulated packet loss Seq={seq}")
                    else:
                        if random.random() < DELAY_PROBABILITY:
                            delay = random.uniform(0, MAX_DELAY)
                            print(
                                f"[DELAY] Simulating delay of {delay:.2f}s for packet Seq={seq}")
                            time.sleep(delay)

                        sock.sendto(packet, addr)
                        print(
                            f"[SEND] Sent DATA packet Seq={seq} Checksum={checksum}")

                    try:
                        sock.settimeout(TIMEOUT)
                        ack_data, _ = sock.recvfrom(BUFFER_SIZE)
                        ack_type, ack_seq, _ = struct.unpack(
                            '!BHI', ack_data[:7])

                        if ack_type == 2 and ack_seq == seq:
                            print(f"[ACK] Received ACK for Seq={ack_seq}")
                            break
                        elif ack_type == 5:
                            print(
                                f"[NACK] Received NACK for Seq={ack_seq}, Resending...")
                            continue

                    except socket.timeout:
                        print(f"[TIMEOUT] Resending packet Seq={seq}")
                        continue

                seq += 1

        eof_packet = struct.pack('!BHI', 4, seq, 0) + b''
        sock.sendto(eof_packet, addr)
        print("[SEND] EOF packet sent. File transfer completed.")
