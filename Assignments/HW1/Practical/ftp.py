from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# تنظیمات حساب کاربری برای FTP
FTP_USERNAME = "admin"
FTP_PASSWORD = "admin"
# دایرکتوری که برای ذخیره و دریافت فایل‌ها استفاده می‌شود.
FTP_DIRECTORY = os.path.join(os.getcwd(), "ftp_files")

# اطمینان از وجود دایرکتوری FTP_DIRECTORY
if not os.path.exists(FTP_DIRECTORY):
    os.makedirs(FTP_DIRECTORY)

# تعریف مجوز‌های کاربری
authorizer = DummyAuthorizer()
# کاربر مجاز به خواندن و نوشتن در دایرکتوری FTP_DIRECTORY
authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, FTP_DIRECTORY, perm="elradfmwMT")
# اجازه دسترسی به کاربران مهمان (اختیاری، اگر نیاز نیست می‌توانید حذف کنید)
authorizer.add_anonymous(FTP_DIRECTORY)

# پیکربندی handler
handler = FTPHandler
handler.authorizer = authorizer

# تنظیمات سرور
address = ("127.0.0.1", 21)  # پورت پیش‌فرض FTP معمولاً 21 است.
server = FTPServer(address, handler)

print(f"FTP Server is running at ftp://{address[0]}:{address[1]}")
server.serve_forever()
