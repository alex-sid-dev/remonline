#!/bin/bash
set -e

DOMAIN="azzlem.ru"
EMAIL="admin@azzlem.ru"
COMPOSE="sudo docker compose -f docker-compose.prod.yaml"

echo "=== SSL initialization for $DOMAIN ==="

# 1. Create dummy certificate so nginx can start
echo "Creating dummy certificate..."
sudo mkdir -p /var/lib/docker/volumes/remonline_certbot_conf/_data/live/$DOMAIN
$COMPOSE run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'" certbot
echo "Dummy certificate created."

# 2. Start nginx with dummy cert
echo "Starting nginx..."
$COMPOSE up -d frontend
sleep 5

# 3. Delete dummy certificate
echo "Removing dummy certificate..."
$COMPOSE run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN && \
  rm -rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

# 4. Request real certificate from Let's Encrypt
echo "Requesting certificate from Let's Encrypt..."
$COMPOSE run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --no-eff-email \
    --force-renewal" certbot

# 5. Reload nginx with real certificate
echo "Reloading nginx..."
$COMPOSE exec frontend nginx -s reload

echo "=== SSL setup complete! https://$DOMAIN is ready ==="
