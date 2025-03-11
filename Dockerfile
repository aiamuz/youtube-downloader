FROM python:3.9

WORKDIR /app

COPY . /app

# نصب پکیج‌ها از requirements.txt
RUN pip install --upgrade pip \
    && pip install --upgrade yt-dlp \
    && pip install -r requirements.txt

CMD ["bash", "start.sh"]
