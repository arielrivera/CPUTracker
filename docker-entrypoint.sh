#!/bin/sh

if [ ! -f /etc/nginx/certs/localhost.crt ] || [ ! -f /etc/nginx/certs/localhost.key ]; then
  echo "SSL certificates not found!"
  exit 1
fi
# Start Nginx
exec nginx -g 'daemon off;'