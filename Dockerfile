FROM python:3.9

WORKDIR /app

COPY . /app

# نصب و به‌روزرسانی پکیج‌ها
RUN pip install --upgrade pip \
    && pip install --upgrade yt-dlp \
    && pip install -r requirements.txt

# ساخت مسیر ذخیره ویدیوها
RUN mkdir -p /app/downloads

# اطمینان از داشتن مجوز برای ذخیره فایل‌ها
RUN chmod -R 777 /app/downloads

CMD ["bash", "start.sh"]
