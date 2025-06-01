

# مستندات کد نمایش IP Fragmentation و حملات شبکه
**نام:** معین  
**نام خانوادگی:** آعلی

**شماره دانشجویی:** 401105561

## توضیح کلی
این کد با استفاده از کتابخانه Scapy، تکنیک‌های مختلف IP Fragmentation و حملات مرتبط با آن را نمایش می‌دهد. این برنامه برای آموزش امنیت شبکه و درک آسیب‌پذیری‌های ناشی از قطعه‌بندی IP طراحی شده است.

## import کتابخانه‌ها

```python
import socket
import sys
import struct
import time
from scapy.all import *
```

- `socket`: برای عملیات شبکه پایه
- `sys`: برای عملیات سیستمی
- `struct`: برای کار با داده‌های باینری
- `time`: برای ایجاد تأخیر
- `scapy.all`: کتابخانه قدرتمند برای ساخت و دستکاری پکت‌های شبکه

## تنظیمات ثابت

```python
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
FRAGMENT_SIZE = 1400
```

- `SERVER_IP`: آدرس IP سرور مقصد (localhost)
- `SERVER_PORT`: پورت سرور مقصد
- `FRAGMENT_SIZE`: اندازه قطعه‌بندی (1400 بایت)

## تابع create_large_payload

```python
def create_large_payload(size=3000):
    pattern = "FRAGMENTATION_TEST_" + "X" * 50 + "_PATTERN_"
    payload = ""
    while len(payload) < size:
        payload += pattern
    return payload[:size]
```

**خط به خط:**
- **خط 2**: ایجاد الگوی پایه شامل رشته تست و 50 کاراکتر X
- **خط 3**: مقداردهی اولیه payload
- **خط 4**: حلقه تا رسیدن به اندازه مطلوب
- **خط 5**: افزودن الگوی پایه
- **خط 6**: برش payload به اندازه دقیق

## تابع send_fragmented_with_different_ttl

```python
def send_fragmented_with_different_ttl():
    print("=== Part 2: TTL Manipulation Demo ===")
    payload = create_large_payload(3000)
    ip_packet = IP(dst=SERVER_IP, ttl=64)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload
    
    print(f"Original packet size: {len(full_packet)} bytes")
    print(f"Payload size: {len(payload)} bytes")
    
    fragments = fragment(full_packet, fragsize=576)
    print(f"Number of fragments created: {len(fragments)}")
    
    ttl_values = [64, 32, 16, 8, 4, 2, 1]
    for i, frag in enumerate(fragments):
        frag[IP].ttl = ttl_values[i] if i < len(ttl_values) else 1
        print(f"Fragment {i+1}: TTL={frag[IP].ttl}, Size={len(frag)} bytes, Flags={frag[IP].flags}, Frag_offset={frag[IP].frag}")
        send(frag, verbose=0)
        time.sleep(0.1)
```

**خط به خط:**
- **خط 2**: چاپ عنوان بخش
- **خط 3**: ایجاد payload 3000 بایتی
- **خط 4**: ساخت هدر IP با TTL=64
- **خط 5**: ساخت هدر UDP
- **خط 6**: ترکیب لایه‌ها با استفاده از عملگر `/` در Scapy
- **خط 8-9**: چاپ اطلاعات پکت اصلی
- **خط 11**: قطعه‌بندی پکت با اندازه 576 بایت
- **خط 12**: چاپ تعداد قطعات
- **خط 14**: لیست مقادیر TTL متفاوت
- **خط 15**: حلقه برای هر قطعه
- **خط 16**: تنظیم TTL متفاوت برای هر قطعه
- **خط 17**: چاپ مشخصات هر قطعه
- **خط 18**: ارسال قطعه
- **خط 19**: تأخیر 0.1 ثانیه

## تابع send_fragmented_with_ttl_1

```python
def send_fragmented_with_ttl_1():
    print("\n=== TTL=1 Test (All fragments) ===")
    payload = create_large_payload(2500)
    ip_packet = IP(dst=SERVER_IP, ttl=1)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload
    
    print(f"Sending packet with TTL=1, size: {len(full_packet)} bytes")
    fragments = fragment(full_packet, fragsize=576)
    print(f"Number of fragments: {len(fragments)}")
    
    for i, frag in enumerate(fragments):
        frag[IP].ttl = 1
        print(f"Fragment {i+1}: TTL={frag[IP].ttl}, Size={len(frag)} bytes")
        send(frag, verbose=0)
        time.sleep(0.1)
```

**خط به خط:**
- **خط 2**: چاپ عنوان تست TTL=1
- **خط 3**: ایجاد payload 2500 بایتی
- **خط 4**: ساخت پکت IP با TTL=1
- **خط 5-6**: ساخت UDP و ترکیب لایه‌ها
- **خط 8**: چاپ اطلاعات ارسال
- **خط 9**: قطعه‌بندی پکت
- **خط 10**: چاپ تعداد قطعات
- **خط 12-16**: حلقه ارسال تمام قطعات با TTL=1

## تابع send_normal_fragmented

```python
def send_normal_fragmented():
    print("\n=== Normal Fragmentation (Control) ===")
    payload = create_large_payload(2000)
    ip_packet = IP(dst=SERVER_IP)
    udp_packet = UDP(dport=SERVER_PORT)
    full_packet = ip_packet / udp_packet / payload
    
    print(f"Sending normal fragmented packet, size: {len(full_packet)} bytes")
    send(full_packet, verbose=0)
```

**خط به خط:**
- **خط 2**: چاپ عنوان قطعه‌بندی عادی
- **خط 3**: ایجاد payload 2000 بایتی
- **خط 4**: ساخت پکت IP عادی (بدون تنظیمات خاص)
- **خط 5-6**: ساخت UDP و ترکیب
- **خط 8**: چاپ اطلاعات
- **خط 9**: ارسال پکت (Scapy خودکار آن را قطعه‌بندی می‌کند)

## تابع demonstrate_insertion_attack

```python
def demonstrate_insertion_attack():
    print("\n=== Insertion Attack Demonstration ===")
    malicious_payload = "MALICIOUS_CONTENT_ATTACK_PAYLOAD"
    legitimate_payload = "LEGITIMATE_NORMAL_CONTENT_DATA"
    
    base_ip = IP(dst=SERVER_IP, id=12345)
    
    # Fragment 1
    frag1 = base_ip.copy()
    frag1.ttl = 64
    frag1.frag = 0
    frag1.flags = "MF"
    packet1 = frag1 / UDP(dport=SERVER_PORT) / legitimate_payload[:20]
    
    # Fragment 2 (Malicious)
    frag2 = base_ip.copy()
    frag2.ttl = 2
    frag2.frag = 0
    frag2.flags = "MF"
    packet2 = frag2 / Raw(malicious_payload[:20])
    
    # Fragment 3
    frag3 = base_ip.copy()
    frag3.ttl = 64
    frag3.frag = 3
    frag3.flags = 0
    packet3 = frag3 / Raw(legitimate_payload[20:])
    
    print(f"Fragment 1: TTL={packet1[IP].ttl}, Offset={packet1[IP].frag}, Flags={packet1[IP].flags}")
    print(f"Fragment 2: TTL={packet2[IP].ttl}, Offset={packet2[IP].frag}, Flags={packet2[IP].flags} (MALICIOUS)")
    print(f"Fragment 3: TTL={packet3[IP].ttl}, Offset={packet3[IP].frag}, Flags={packet3[IP].flags}")
    
    send(packet1, verbose=0)
    time.sleep(0.5)
    send(packet2, verbose=0)
    time.sleep(0.5)
    send(packet3, verbose=0)
```

**خط به خط:**
- **خط 2**: چاپ عنوان حمله Insertion
- **خط 3-4**: تعریف محتوای مخرب و مشروع
- **خط 6**: ساخت پکت IP پایه با شناسه 12345
- **خط 8-12**: ساخت قطعه اول (مشروع) با offset=0 و flag MF (More Fragments)
- **خط 14-18**: ساخت قطعه دوم (مخرب) با TTL پایین و همان offset
- **خط 20-24**: ساخت قطعه سوم (ادامه مشروع) با offset=3
- **خط 26-28**: چاپ مشخصات هر قطعه
- **خط 30-34**: ارسال قطعات با فاصله زمانی

## بخش اصلی برنامه

```python
if __name__ == "__main__":
    try:
        print("\n1. Different TTL values per fragment")
        send_fragmented_with_different_ttl()
        time.sleep(2)
        
        print("\n2. All fragments with TTL=1")
        send_fragmented_with_ttl_1()
        time.sleep(2)
        
        print("\n3. Normal fragmentation (comparison)")
        send_normal_fragmented()
        time.sleep(2)
        
        print("\n4. Insertion attack demonstration")
        demonstrate_insertion_attack()
    except Exception as e:
        print(e)
```

**خط به خط:**
- **خط 1**: بررسی اجرای مستقیم فایل
- **خط 2**: شروع بلوک try برای مدیریت خطا
- **خط 3-5**: اجرای تست TTL متفاوت و تأخیر 2 ثانیه
- **خط 7-9**: اجرای تست TTL=1 و تأخیر
- **خط 11-13**: اجرای قطعه‌بندی عادی و تأخیر
- **خط 15-16**: اجرای حمله Insertion
- **خط 17-18**: مدیریت خطاهای احتمالی

## کاربرد کد

این کد چهار سناریوی مختلف را نمایش می‌دهد:

1. **TTL Manipulation**: تنظیم TTL متفاوت برای هر قطعه
2. **TTL Expiration**: ارسال همه قطعات با TTL=1
3. **Normal Fragmentation**: قطعه‌بندی عادی برای مقایسه
4. **Insertion Attack**: حمله درج محتوای مخرب
