import socket
import threading
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ftplib import FTP


# Server configuration
HOST = '127.0.0.1'
PORT = 12345


# FTP configuration
FTP_SERVER = "ftp.dlptest.com"
FTP_USERNAME = "dlpuser@dlptest.com"
FTP_PASSWORD = "eUj8GeW55SvYaswqUyDSm5v6N"
FTP_DIRECTORY = 'ftp_files'  # Folder where files will be uploaded

# Classroom state
clients = {}  # Format: {client_socket: {"id": id, "name": name}}
client_id_counter = 1


# Ensure the FTP directory exists
if not os.path.exists(FTP_DIRECTORY):
    os.makedirs(FTP_DIRECTORY)


def broadcast(message):
    """Send a message to all connected clients."""
    for client in clients:
        try:
           #TODO
        except:
            pass



# Function to list files on the FTP server
def list_files():
    ftp = FTP()
    #TODO : List files in the FTP_DIRECTORY 

    return files

# Function to download a file from the FTP server
def download_file(filename):
    try:
        ftp = FTP()

        #TODO :  # Download the file


        print(f"Downloaded {filename} successfully.")
        return file_content
    except Exception as e:
        print(f"Failed to download file from FTP server: {e}")
        return None


def server_command_interface():
    """Allow server admin to send messages or issue commands to clients."""
    while True:
        """ server can send  messages to clients, can see list of files and can download a file"""

        command = input("\nEnter command (/chat, /listdir ,/download): ")

        if command.startswith("/chat"):
            msg = ...
            broadcast(json.dumps({"type": "chat", "from": "Server", "message": msg}))
            print(f"Sent message: {msg}")

        elif command.startswith("/listdir"):
            files = ...
            files_str = "\n".join(files) if isinstance(files, list) else files
            print(f"Files in FTP:\n{files_str}")

        elif command.startswith("/download"):
            # server should be able to download a file a(print content of that)
            #TODO 
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
    welcome_message = f"Welcome to the virtual classroom! Your ID is {client_id}."
    print(f"Sending to client {client_id}: {welcome_message}")
    # TODO : send welcome message client


    # Broadcast to all clients that a new student has joined
    broad_msg=f"{clients[client]['name']} has joined the classroom."
    #TODO
    
    try:
        while True:
            # TODO : get data from client
            data = ...
            if not data:
                break

            message = json.loads(data)
            print(f"\nReceived from client {client_id}: {data}")

            if message["type"] == "chat":
                # Broadcast chat message to all clients
                data=json.dumps({
                    "type": "chat",
                    "from": clients[client]["name"],
                    "message": message["message"]
                })
                #TODO
                
            elif message["type"] == "email_status":
                # TODO: for simplify, just check status of msg and if is equal to "sent", send below receive msg to client
               
                data=json.dumps({
                    "type": "email_status",
                    "status": "success",
                    "message": f"Email Received"
                }).encode('utf-8')


            elif message["type"] == "upload":
                # Handle file upload to FTP
                filename = message["filename"]
                status_upload = message["status_upload"]
                if status_upload==200:

                    #TODO : server should see list of files and check the filename exist or not
                    # if exists, send a msg with status="success" else send status="error" and proper message
                    ....
                    data=json.dumps({
                        "type": "upload_status",
                        "status": "success",
                        "message": f"File {filename} has been uploaded to FTP server Successfully."
                    }).encode('utf-8')
                    ...


            elif message["type"] == "download":
                # Handle file download from FTP
                filename = message["filename"]
                 
                #TODO : you should see list of files and check the filename exist or not
                # Then if exists, send a msg with status="ok" for client to download file 
                # else send with status="error"
                ...
                data=json.dumps({
                        "type": "download_status",
                        "filename": filename,
                        "status": "ok",
                        "message": f"Ready to download file {filename}."

                }).encode('utf-8')

                ....

    except Exception as e:
        print(f"Error: {e}")
    finally:
        del clients[client]
        client.close()
        # TODO: broadcast a msg that a student has left the classroom.
        ....


def start_server():
    """Start the server and accept client connections."""
    #TODO
    
    ...
    server=....
    print(f"Server started on {HOST}:{PORT}")

    threading.Thread(target=server_command_interface, daemon=True).start()

    while True:
        client, address = server.accept()
        # start a new thread for each client that connect
        ....

if __name__ == "__main__":
    start_server()