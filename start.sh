#!/bin/bash

# حذف ویدیوهای قدیمی‌تر از 6 ساعت
find /app/downloads -type f -mmin +360 -exec rm -f {} \;

# اجرای Gunicorn به جای Python مستقیم
gunicorn --bind 0.0.0.0:5000 server:app
