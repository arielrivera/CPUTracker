#!/bin/sh


# # Check if SSL certificates are present
# if [ ! -f /etc/ssl/certs/cert.pem ] || [ ! -f /etc/ssl/private/key.pem ]; then
#   echo "SSL certificates not found!"
#   exit 1
# fi

# Start Nginx
exec nginx -g 'daemon off;'