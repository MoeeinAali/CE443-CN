import socket
import threading
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from ftplib import FTP

HOST = '127.0.0.1'
PORT = 12345

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'test@gmail.com'
SMTP_PASSWORD = 'password'

FTP_SERVER = "127.0.0.1"
FTP_USERNAME = "admin"
FTP_PASSWORD = "admin"
FTP_DIRECTORY = 'ftp_files'


def receive_messages(client):
    while True:
        try:
            data = client.recv(10 * 1024 * 1024)
            if not data:
                break
            try:
                message = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                print("Received invalid JSON message.")
                continue

            if message.get("type") == "download_response":
                if message.get("status") == "success":
                    filename = message["filename"]
                    content_b64 = message["content"]
                    try:
                        file_bytes = base64.b64decode(content_b64)
                        with open(filename, "wb") as f:
                            f.write(file_bytes)
                        print(f"\nFile '{filename}' downloaded and saved successfully.")
                    except Exception as e:
                        print(f"\nError saving '{filename}': {e}")
                else:
                    print(f"\nDownload failed: {message.get('message')}")
                continue

            print(f"\nReceived from server: {message}")

        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = 'moeeeinaali@gmail.com'
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, 'moeeeinaali@gmail.com', msg.as_string())
        print(f"Email sent to moeeeinaali@gmail.com")
    except Exception as e:
        print(f"Failed to send email: {e}")


def upload_to_ftp(filename):
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


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("Connected to the classroom.")

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    try:
        while True:
            user_input = input("\nEnter a command (/chat, /email, /upload, /download): ")

            if user_input.startswith("/chat"):
                message_text = user_input[len("/chat "):].strip()
                client.send(json.dumps({
                    "type": "chat",
                    "message": message_text
                }).encode('utf-8'))

            elif user_input.startswith("/email"):
                parts = user_input[len("/email "):].split(" ", 1)
                if len(parts) == 2:
                    subject, body = parts
                    send_email(subject, body)
                    client.send(json.dumps({
                        "type": "email_status",
                        "status": "sent"
                    }).encode('utf-8'))
                else:
                    print("Invalid email format. Use: /email <subject> <body>")

            elif user_input.startswith("/upload"):
                filename = user_input[len("/upload "):].strip()
                if os.path.exists(filename):
                    upload_to_ftp(filename)
                else:
                    print(f"File {filename} not found.")

            elif user_input.startswith("/download"):
                filename = user_input[len("/download "):].strip()
                client.send(json.dumps({
                    "type": "download",
                    "filename": filename
                }).encode('utf-8'))

            else:
                print("Invalid command.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Disconnected from classroom.")


start_client()
