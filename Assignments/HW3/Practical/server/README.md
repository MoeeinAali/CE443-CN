# مستندات کد UDP Server - دریافت و پردازش پیام‌های شبکه

**نام:** معین  
**نام خانوادگی:** آعلی

**شماره دانشجویی:** 401105561


## توضیح کلی
این کد یک UDP Server ساده است که برای دریافت و پردازش پیام‌های ارسالی از کلاینت‌ها طراحی شده است. این سرور می‌تواند پیام‌های بزرگ و قطعه‌بندی شده را دریافت کرده و تأییدیه مناسب ارسال کند.

## import کتابخانه

```python
import socket
```

- `socket`: کتابخانه اصلی برای برقراری ارتباطات شبکه در Python

## ایجاد و تنظیم Socket

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 9999))
print("Server started on localhost:9999")
```

**خط به خط:**
- **خط 1**: ایجاد UDP socket
  - `socket.AF_INET`: استفاده از پروتکل IPv4
  - `socket.SOCK_DGRAM`: استفاده از پروتکل UDP (بدون اتصال)
- **خط 2**: اتصال socket به آدرس و پورت مشخص
  - `'localhost'`: آدرس IP محلی (127.0.0.1)
  - `9999`: شماره پورت که سرور روی آن گوش می‌دهد
- **خط 3**: چاپ پیام شروع سرور

## حلقه اصلی سرور

```python
try:
    while True:
        data, client_address = server_socket.recvfrom(65535)
        message = data.decode('utf-8', errors='ignore')
        
        print(f"Received {len(data)} bytes from {client_address}")
        print(f"Message: {message}")
        
        ack_message = f"ACK: Received {len(data)} bytes"
        server_socket.sendto(ack_message.encode(), client_address)
```

**خط به خط:**
- **خط 1**: شروع بلوک try برای مدیریت خطاها
- **خط 2**: حلقه بی‌نهایت برای دریافت مداوم پیام‌ها
- **خط 3**: دریافت داده و آدرس کلاینت
  - `65535`: حداکثر اندازه بافر دریافت (64KB)
  - `data`: داده‌های دریافتی به صورت bytes
  - `client_address`: آدرس IP و پورت کلاینت فرستنده
- **خط 4**: تبدیل bytes به string
  - `'utf-8'`: انکودینگ استاندارد
  - `errors='ignore'`: نادیده گیری خطاهای انکودینگ
- **خط 6**: چاپ تعداد بایت‌های دریافتی و آدرس فرستنده
- **خط 7**: چاپ محتوای پیام
- **خط 9**: ساخت پیام تأییدیه (ACK)
- **خط 10**: ارسال تأییدیه به کلاینت
  - `.encode()`: تبدیل string به bytes برای ارسال

## مدیریت خروج و بستن Socket

```python
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server_socket.close()
    print("Server socket closed.")
```

**خط به خط:**
- **خط 1**: گرفتن سیگنال Ctrl+C برای خروج از برنامه
- **خط 2**: چاپ پیام خاموش شدن سرور
- **خط 3**: بلوک finally که همیشه اجرا می‌شود
- **خط 4**: بستن socket سرور برای آزادسازی منابع
- **خط 5**: چاپ تأیید بستن socket

## ویژگی‌های کلیدی

### 1. بافر بزرگ دریافت
```python
data, client_address = server_socket.recvfrom(65535)
```
- استفاده از بافر 64KB برای دریافت پیام‌های بزرگ
- امکان دریافت پکت‌های قطعه‌بندی شده

### 2. مدیریت خطای انکودینگ
```python
message = data.decode('utf-8', errors='ignore')
```
- استفاده از `errors='ignore'` برای جلوگیری از crash در صورت داده‌های نامعتبر
- امکان پردازش داده‌های باینری یا خراب

### 3. سیستم تأییدیه (ACK)
```python
ack_message = f"ACK: Received {len(data)} bytes"
server_socket.sendto(ack_message.encode(), client_address)
```
- ارسال تأییدیه به کلاینت برای اطمینان از دریافت
- شامل اطلاعات تعداد بایت‌های دریافتی

