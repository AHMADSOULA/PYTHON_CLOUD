# استخدام صورة Playwright الرسمية التي تحتوي على كل ما يحتاجه المتصفح
FROM mcr.microsoft.com/playwright/python:v1.64.1-noble

# تحديد مسار العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# التأكد من تثبيت متصفح Chromium والاعتماديات الخاصة به
RUN playwright install chromium

# نسخ باقي ملفات المشروع (GC.py وغيرها)
COPY . .

# أمر تشغيل البوت
CMD ["python", "GC.py"]
