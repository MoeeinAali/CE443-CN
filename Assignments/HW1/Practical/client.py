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

# SMTP configuration (for Gmail; fill in your credentials if testing email)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''  # Replace with your email if needed
SMTP_PASSWORD = ''  # Replace with your email password if needed

# FTP configuration
FTP_SERVER = "127.0.0.1"
FTP_USERNAME = "admin"
FTP_PASSWORD = "admin"
FTP_DIRECTORY = 'ftp_files'


def receive_messages(client):
    """Handle incoming messages from the server."""
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            try:
                message = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                print("Received invalid JSON message.")
                continue
            print(f"\nReceived from server: {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def send_email(to, subject, body):
    """Send an email using SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to  # In this exercise the student's email is sent to the server's address.
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to, msg.as_string())
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def upload_to_ftp(filename):
    """Upload a file to the FTP server."""
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)
        with open(filename, "rb") as file_obj:
            ftp.storbinary(f"STOR {os.path.basename(filename)}", file_obj)
        ftp.quit()
        print(f"File {filename} uploaded successfully.")
        return True
    except Exception as e:
        print(f"FTP upload error: {e}")
        return False


def download_file_ftp(filename):
    """Download a file from the FTP server and return its content."""
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)
        ftp.cwd(FTP_DIRECTORY)
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


def start_client():
    """Connect to the server and interact with the classroom."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("Connected to the classroom.")
    
    # Start a thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    try:
        while True:
            user_input = input("\nEnter a command (/chat, /email, /upload, /download): ")

            if user_input.startswith("/chat"):
                message_text = user_input[len("/chat "):].strip()
                data = json.dumps({
                    "type": "chat",
                    "message": message_text
                }).encode('utf-8')
                try:
                    client.send(data)
                except Exception as e:
                    print(f"Error sending chat message: {e}")

            elif user_input.startswith("/email"):
                # Expected format: /email <to> <subject> <body>
                parts = user_input[len("/email "):].split(" ", 2)
                if len(parts) == 3:
                    to, subject, body = parts
                    # In this design the client sends a notification that email is sent.
                    # Optionally, you can call send_email here.
                    send_email(to, subject, body)
                    data = json.dumps({
                        "type": "email_status",
                        "status": "sent"
                    }).encode('utf-8')
                    try:
                        client.send(data)
                    except Exception as e:
                        print(f"Error sending email status: {e}")
                else:
                    print("Invalid email format. Use: /email <to> <subject> <body>")

            elif user_input.startswith("/upload"):
                filename = user_input[len("/upload "):].strip()
                if os.path.exists(filename):
                    upload_to_ftp(filename)
                    # status_upload = 200 if upload_to_ftp(filename) else 500
                    # data = json.dumps({
                    #     "type": "upload",
                    #     "filename": os.path.basename(filename),
                    #     "status_upload": status_upload
                    # }).encode('utf-8')
                    # try:
                    #     client.send(data)
                    # except Exception as e:
                    #     print(f"Error sending upload message: {e}")
                else:
                    print(f"File {filename} not found.")

            elif user_input.startswith("/download"):
                filename = user_input[len("/download "):].strip()
                # Inform server that we want to download file
                data = json.dumps({
                    "type": "download",
                    "filename": filename
                }).encode('utf-8')
                try:
                    client.send(data)
                except Exception as e:
                    print(f"Error sending download request: {e}")

                # Wait for server's response. In this example we use a blocking recv.
                # In a robust design, you might have a unique identifier for requests.
                response_data = client.recv(1024)
                if not response_data:
                    print("No response from server.")
                    continue
                try:
                    response = json.loads(response_data.decode('utf-8'))
                except json.JSONDecodeError:
                    print("Invalid response from server.")
                    continue

                if response["type"] == "download_status" and response["status"] == "OK":
                    print(f"Server is ready to download {filename}. Proceeding...")
                    file_content = download_file_ftp(filename)
                    if file_content:
                        print(f"File content received:\n{file_content.decode('utf-8', errors='replace')}")
                    else:
                        print("Error downloading file content from FTP server.")
                else:
                    print("Failed to receive OK from server for downloading the file:")
                    print(response.get("message", "No message"))
            else:
                print("Invalid command.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Disconnected from classroom.")


if __name__ == "__main__":
    start_client()
