import socket
import threading
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ftplib import FTP

# Server configuration
HOST = '127.0.0.1'
PORT = 12345


# SMTP configuration (for Gmail)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''  # Replace with your email
SMTP_PASSWORD = ''  # Replace with your email password


# FTP configuration
FTP_SERVER = "ftp.dlptest.com" #  (you can replace with real IP or domain or Local server)
FTP_USERNAME = "dlpuser@dlptest.com"
FTP_PASSWORD = "eUj8GeW55SvYaswqUyDSm5v6N"
FTP_DIRECTORY = 'ftp_files'  # Folder where files will be uploaded


def receive_messages(client):
    """Handle incoming messages from the server."""
    while True:
        try:
            data = ...
            if not data:
                break
            print(f"\nReceived from server: {data}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


# Function to send email(client want send email(plain text) to server email)
# you should consider an email address for server and send msg to it
def send_email(to, subject, body):
    """Send an email using SMTP."""
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
           # TODO : send email to server's email address
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to upload a file to the FTP server
def upload_to_ftp(filename):
    ftp = FTP(FTP_SERVER)
    #TODO 
    print(f"File {filename} uploaded successfully.")

# Function to download a file from the FTP server
def download_file(filename):
    try:
        ftp = FTP()
         #TODO
        print(f"Downloaded {filename} successfully.")
        return file_content
    except Exception as e:
        print(f"Failed to download file from FTP server: {e}")
        return None

def start_client():
    """Connect to the server and interact with the classroom."""
    #TODO open socket and connect to HOST with PORT
    client = ...

    #TODO :Start a thread to receive messages


    try:
        while True:
            # Get user input
            user_input = input("Enter a command (/chat, /email, /upload, /download): ")
            if user_input.startswith("/chat"):
                # Send chat message
                message = user_input[len("/chat "):]
                data=json.dumps({
                    "type": "chat",
                    "message": message
                }).encode('utf-8')
                # TODO : send data to server

            elif user_input.startswith("/email"):
                # Send email
                parts = user_input[len("/email "):].split(" ", 2)
                if len(parts) == 3:
                    to, subject, body = parts
                    data=json.dumps({
                        "type": "email_status",
                        "status": "sent"
                    }).encode('utf-8')

                    # TODO : send data to server
                    # if email sent successfully, send a message of type "email_status" with status="sent" to server
                else:
                    print("Invalid email format. Use: /email <to> <subject> <body>")

            elif user_input.startswith("/upload"):
                # Upload file to FTP
                filename = user_input[len("/upload "):]
                try:
                 #TODO: if file upload is ok , send a msg with status_upload=200 otherwise with status_upload=500 
                 data=json.dumps({
                            "type": "upload",
                            "filename": filename,
                            "status_upload": 200
                        }).encode('utf-8')
                ...

                except FileNotFoundError:
                    print(f"File {filename} not found.")

            elif user_input.startswith("/download"):
                # Download file from FTP
                filename = user_input[len("/download "):]
                 #TODO : send a message of type download to server with filename and wait to get response of type download_status status="ok"
                        ....
                  # Wait for server's OK response
                response = ...
                message = ..
                if message["type"] == "download_status" and message["status"] == "OK":
                    print(f"Server is ready to download {filename}. Now proceeding to download the file from FTP.")
                     #TODO : download file 
                    file_content = ....
                    if file_content:
                        print(f"File content received:\n{file_content.decode('utf-8')}")
                else:
                    print("Failed to receive OK from server for downloading the file.")
            else:
                print("Invalid command.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()