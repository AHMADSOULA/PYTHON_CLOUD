FROM mcr.microsoft.com/playwright/python:v1.64.1-noble

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفح Chromium واعتماديات النظام
RUN playwright install --with-deps chromium

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "GC.py"]
