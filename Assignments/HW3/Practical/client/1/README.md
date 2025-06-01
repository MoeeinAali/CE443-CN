# مستندات کد UDP Client - نمایش IP Fragmentation

**نام:** معین  
**نام خانوادگی:** آعلی

**شماره دانشجویی:** 401105561

## توضیح کلی
این کد یک UDP Client است که برای نمایش مفهوم IP Fragmentation طراحی شده است. این برنامه پیام‌های بزرگ را به سرور ارسال می‌کند تا نحوه تقسیم پکت‌های بزرگ در شبکه را بررسی کند.

## import کتابخانه‌ها

```python
import socket
import time
```

- `socket`: برای ایجاد و مدیریت اتصالات شبکه
- `time`: برای ایجاد تأخیر بین ارسال پیام‌ها

## تنظیمات ثابت

```python
SERVER_ADDRESS = ('localhost', 9999)
FRAGMENT_SIZE = 1400
```

- `SERVER_ADDRESS`: آدرس و پورت سرور مقصد (localhost روی پورت 9999)
- `FRAGMENT_SIZE`: اندازه قطعه‌بندی (1400 بایت - نزدیک به MTU استاندارد)

## تابع create_large_message

```python
def create_large_message(size=5000):
    message = "A" * 100 + "B" * 100 + "C" * 100 + "D" * 100 + "E" * 100
    base_pattern = message
   
    while len(message) < size:
        message += base_pattern
   
    return message[:size]
```

**خط به خط:**
- **خط 1**: تعریف تابع با پارامتر پیش‌فرض 5000 بایت
- **خط 2**: ایجاد پیام پایه با 500 کاراکتر (100 عدد از هر حرف A, B, C, D, E)
- **خط 3**: ذخیره الگوی پایه
- **خط 5**: حلقه تا رسیدن به اندازه مطلوب
- **خط 6**: افزودن الگوی پایه به پیام
- **خط 8**: برش پیام به اندازه دقیق مورد نظر

## تابع send_large_message

```python
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
            ack_data, * = client_socket.recvfrom(1024)
            print(f"Received ACK: {ack_data.decode()}")
        except socket.timeout:
            print("No acknowledgment received (timeout)")
       
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        client_socket.close()
        print("Client socket closed.")
```

**خط به خط:**
- **خط 2**: ایجاد UDP socket (AF_INET برای IPv4، SOCK_DGRAM برای UDP)
- **خط 5**: ایجاد پیام بزرگ با اندازه FRAGMENT_SIZE
- **خط 6**: تبدیل رشته به bytes با encoding UTF-8
- **خط 8**: چاپ اطلاعات ارسال
- **خط 10**: ارسال پیام به سرور
- **خط 11**: تأیید ارسال موفق
- **خط 13**: تنظیم timeout 5 ثانیه برای دریافت پاسخ
- **خط 15**: دریافت تأییدیه از سرور (ACK)
- **خط 16**: چاپ پیام تأییدیه دریافتی
- **خط 17-18**: مدیریت timeout اگر پاسخی نیاید
- **خط 20-21**: مدیریت خطاها
- **خط 23-24**: بستن socket در نهایت

## تابع send_multiple_sizes

```python
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
```

**خط به خط:**
- **خط 2**: لیست اندازه‌های مختلف پیام برای تست
- **خط 4**: حلقه برای هر اندازه
- **خط 5**: چاپ جداکننده بصری
- **خط 6**: چاپ اندازه فعلی
- **خط 8**: ایجاد socket جدید برای هر ارسال
- **خط 11**: ایجاد پیام با اندازه مشخص
- **خط 12**: تبدیل به bytes
- **خط 14**: ارسال پیام
- **خط 15**: چاپ تعداد بایت‌های ارسالی
- **خط 16**: تأخیر 1 ثانیه بین ارسال‌ها
- **خط 18-19**: مدیریت خطا
- **خط 21**: بستن socket

## بخش اصلی برنامه

```python
print("UDP Client - IP Fragmentation Demo")
print(f"Fragment size setting: {FRAGMENT_SIZE} bytes")
choice = input("\n1. Send single large message\n2. Send multiple different sizes\nChoice (1/2): ")

if choice == "1":
    send_large_message()
elif choice == "2":
    send_multiple_sizes()
else:
    print("Invalid choice")
```

**خط به خط:**
- **خط 1**: چاپ عنوان برنامه
- **خط 2**: نمایش تنظیمات اندازه قطعه‌بندی
- **خط 3**: دریافت انتخاب کاربر (منوی تعاملی)
- **خط 5-6**: اگر انتخاب 1، ارسال یک پیام بزرگ
- **خط 7-8**: اگر انتخاب 2، ارسال پیام‌های متعدد با اندازه‌های مختلف
- **خط 9-10**: پیام خطا برای انتخاب نامعتبر

## هدف کد
این کد برای آزمایش و نمایش IP Fragmentation طراحی شده است. وقتی پیام‌های بزرگ‌تر از MTU شبکه (معمولاً 1500 بایت) ارسال می‌شوند، پروتکل IP آن‌ها را به قطعات کوچک‌تر تقسیم می‌کند. این کد این فرآیند را شبیه‌سازی و بررسی می‌کند.