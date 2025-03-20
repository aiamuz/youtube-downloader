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

# کپی کردن cookies.txt
COPY cookies.txt /app/cookies.txt
RUN chmod 644 /app/cookies.txt  # دادن مجوز خواندن به فایل cookies.txt

CMD ["bash", "start.sh"]
