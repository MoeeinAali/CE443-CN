import socket
import time

SERVER_ADDRESS = ('localhost', 9999)
FRAGMENT_SIZE = 16

def create_large_message(size=5000):
    message = "A" * 100 + "B" * 100 + "C" * 100 + "D" * 100 + "E" * 100
    base_pattern = message
    
    while len(message) < size:
        message += base_pattern
    
    return message[:size]

def send_large_message():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        large_message = create_large_message(FRAGMENT_SIZE)
        message_bytes = large_message.encode('utf-8')
        
        print(f"Sending large message of size {len(message_bytes)} bytes to {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
        
        client_socket.sendto(message_bytes, SERVER_ADDRESS)
        print("Message sent successfully!")
        
        client_socket.settimeout(5.0)
        try:
            ack_data, _ = client_socket.recvfrom(1024)
            print(f"Received ACK: {ack_data.decode()}")
        except socket.timeout:
            print("No acknowledgment received (timeout)")
        
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        client_socket.close()
        print("Client socket closed.")

def send_multiple_sizes():
    sizes = [500, 1000, 1500, 2000, 3000, 5000]
    
    for size in sizes:
        print(f"\n{'='*50}")
        print(f"Sending message of size: {size} bytes")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            message = create_large_message(size)
            message_bytes = message.encode('utf-8')
            
            client_socket.sendto(message_bytes, SERVER_ADDRESS)
            print(f"Sent {len(message_bytes)} bytes")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error sending {size} byte message: {e}")
        finally:
            client_socket.close()

print("UDP Client - IP Fragmentation Demo")
print(f"Fragment size setting: {FRAGMENT_SIZE} bytes")

choice = input("\n1. Send single large message\n2. Send multiple different sizes\nChoice (1/2): ")

if choice == "1":
    send_large_message()
elif choice == "2":
    send_multiple_sizes()
else:
    print("Invalid choice")
