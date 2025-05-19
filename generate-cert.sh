#!/bin/sh
mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt