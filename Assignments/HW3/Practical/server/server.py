import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 9999))
print("Server started on localhost:9999")

try:
    while True:
        data, client_address = server_socket.recvfrom(65535)
        message = data.decode('utf-8', errors='ignore')
        print(f"Received {len(data)} bytes from {client_address}")
        print(f"Message: {message}")
        ack_message = f"ACK: Received {len(data)} bytes"
        server_socket.sendto(ack_message.encode(), client_address)
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server_socket.close()
    print("Server socket closed.")
