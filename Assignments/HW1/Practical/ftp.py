from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

FTP_USERNAME = "admin"
FTP_PASSWORD = "admin"

FTP_DIRECTORY = os.path.join(os.getcwd(), "ftp_files")

if not os.path.exists(FTP_DIRECTORY):
    os.makedirs(FTP_DIRECTORY)

authorizer = DummyAuthorizer()

authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, FTP_DIRECTORY, perm="elradfmwMT")

authorizer.add_anonymous(FTP_DIRECTORY)

handler = FTPHandler
handler.authorizer = authorizer

address = ("127.0.0.1", 21) 
server = FTPServer(address, handler)

print(f"FTP Server is running at ftp://{address[0]}:{address[1]}")
server.serve_forever()
