#!/bin/bash
set -e

DOMAIN="azzlem.ru"
EMAIL="admin@azzlem.ru"
COMPOSE="sudo docker compose -f docker-compose.prod.yaml"

echo "=== SSL initialization for $DOMAIN ==="

# 1. Create dummy certificate so nginx can start
echo "Creating dummy certificate..."
$COMPOSE run --rm --entrypoint "\
  sh -c \"mkdir -p /etc/letsencrypt/live/$DOMAIN && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'\"" certbot
echo "Dummy certificate created."

# 2. Start/restart nginx with dummy cert
echo "Starting nginx..."
$COMPOSE up -d frontend
sleep 5
echo "Nginx is running."

# 3. Request real certificate (overwrites dummy)
echo "Requesting certificate from Let's Encrypt..."
$COMPOSE run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --no-eff-email \
    --force-renewal" certbot

# 4. Reload nginx with real certificate
echo "Reloading nginx..."
$COMPOSE exec frontend nginx -s reload

echo "=== SSL setup complete! https://$DOMAIN is ready ==="
