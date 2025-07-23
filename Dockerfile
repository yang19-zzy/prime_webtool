# Use Python 3.13 base image
FROM python:alpine

WORKDIR /app

RUN apk add --no-cache openssl

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "run:app"]
