import socket
import threading
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ftplib import FTP

# Server configuration
HOST = '127.0.0.1'
PORT = 12345

# FTP configuration
FTP_SERVER = "127.0.0.1"
FTP_USERNAME = "admin"
FTP_PASSWORD = "admin"
FTP_DIRECTORY = 'ftp_files'  # Folder where files will be uploaded

# Classroom state
clients = {}  # Format: {client_socket: {"id": id, "name": name}}
client_id_counter = 1

# Ensure the FTP directory exists (for local backup use if needed)
if not os.path.exists(FTP_DIRECTORY):
    os.makedirs(FTP_DIRECTORY)


def broadcast(message, exclude_client=None):
    """Send a message to all connected clients except optional exclude_client."""
    for client in list(clients.keys()):
        if client == exclude_client:
            continue
        try:
            client.send(message)
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")


def list_files():
    """List files in the FTP_DIRECTORY on the FTP server."""
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)
        files = ftp.nlst()
        ftp.quit()
        return files
    except Exception as e:
        print(f"FTP list_files error: {e}")
        return []


def download_file(filename):
    """Download the file from the FTP server and return its content."""
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)

        # Retrieve file content into bytes
        file_content = bytearray()
        def handle_binary(more_data):
            file_content.extend(more_data)
        ftp.retrbinary(f"RETR {filename}", handle_binary)
        ftp.quit()
        print(f"Downloaded {filename} successfully.")
        return bytes(file_content)
    except Exception as e:
        print(f"Failed to download file from FTP server: {e}")
        return None


def server_command_interface():
    """Allow server admin to send messages or issue commands to clients."""
    while True:
        command = input("\nEnter command (/chat, /listdir, /download): ")

        if command.startswith("/chat"):
            # Extract message after the command
            msg = command[len("/chat "):].strip()
            payload = json.dumps({"type": "chat", "from": "Server", "message": msg}).encode('utf-8')
            broadcast(payload)
            print(f"Sent message: {msg}")

        elif command.startswith("/listdir"):
            files = list_files()
            files_str = "-".join(files)
            print(f"Files in FTP: {files_str}")

        elif command.startswith("/download"):
            # Extract filename and attempt download
            parts = command.split(" ", 1)
            if len(parts) < 2:
                print("Usage: /download <filename>")
                continue
            filename = parts[1].strip()
            files = list_files()
            if filename in files:
                file_content = download_file(filename)
                if file_content:
                    with open(filename, "wb") as file:
                        file.write(file_content)  # Remove decode since we want to write bytes
                else:
                    print("Error downloading file.")
            else:
                print(f"File {filename} does not exist on FTP server.")
        else:
            print("Invalid command. Use /chat <message> or /listdir or /download <filename>")


def handle_client(client, address):
    """Handle communication with a single client."""
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1
    clients[client] = {"id": client_id, "name": f"Student {client_id}"}

    print(f"New connection from {address} with ID {client_id}")

    # Send welcome message to the client
    welcome_message = {
        "type": "welcome",
        "message": f"Welcome to the virtual classroom! Your ID is {client_id}."
    }
    try:
        client.send(json.dumps(welcome_message).encode('utf-8'))
    except Exception as e:
        print(f"Error sending welcome message to client {client_id}: {e}")

    broad_msg = {
        "type": "system",
        "message": f"{clients[client]['name']} has joined the classroom."
    }
    broadcast(json.dumps(broad_msg).encode('utf-8'), exclude_client=client)

    try:
        while True:
            data = client.recv(1024)
            if not data:
                break

            try:
                message = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                print("Received invalid JSON data.")
                continue

            print(f"\nReceived from client {client_id}: {message}")

            if message["type"] == "chat":
                data_to_send = json.dumps({
                    "type": "chat",
                    "from": clients[client]["name"],
                    "message": message["message"]
                }).encode('utf-8')
                broadcast(data_to_send)

            elif message["type"] == "email_status":
                response = json.dumps({
                    "type": "email_status",
                    "status": "success",
                    "message": "Email Received"
                }).encode('utf-8')
                client.send(response)

            elif message["type"] == "upload":
                filename = message["filename"]
                status_upload = message["status_upload"]
                files = list_files()
                if status_upload == 200 and filename in files:
                    response = {
                        "type": "upload_status",
                        "status": "success",
                        "message": f"File {filename} has been uploaded to FTP server Successfully."
                    }
                else:
                    response = {
                        "type": "upload_status",
                        "status": "error",
                        "message": f"File {filename} upload failed or not found on FTP server."
                    }
                client.send(json.dumps(response).encode('utf-8'))

            elif message["type"] == "download":
                filename = message["filename"]
                files = list_files()
                if filename in files:
                    response = {
                        "type": "download_status",
                        "filename": filename,
                        "status": "OK",
                        "message": f"Ready to download file {filename}."
                    }
                else:
                    response = {
                        "type": "download_status",
                        "filename": filename,
                        "status": "error",
                        "message": f"File {filename} does not exist on FTP server."
                    }
                client.send(json.dumps(response).encode('utf-8'))
            else:
                print("Received unrecognized message type.")
    except Exception as e:
        print(f"Error in client {client_id} thread: {e}")
    finally:
        del clients[client]
        client.close()
        leave_msg = {
            "type": "system",
            "message": f"Student {client_id} has left the classroom."
        }
        broadcast(json.dumps(leave_msg).encode('utf-8'))
        print(f"Connection with client {client_id} closed.")


def start_server():
    """Start the server and accept client connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)  
    print(f"Server started on {HOST}:{PORT}")

    threading.Thread(target=server_command_interface, daemon=True).start()  

    while True:
        try:
            client, address = server.accept()
            threading.Thread(target=handle_client, args=(client, address), daemon=True).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break

    server.close()


if __name__ == "__main__":
    start_server()
