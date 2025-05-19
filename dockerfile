# Use Python 3.13 base image
FROM python:alpine

WORKDIR /app

RUN apk add --no-cache openssl

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]