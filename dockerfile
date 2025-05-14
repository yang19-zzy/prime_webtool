# Use Python 3.13 base image
FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./nginx/certs/selfsigned.key \
    -out ./nginx/certs/selfsigned.crt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]