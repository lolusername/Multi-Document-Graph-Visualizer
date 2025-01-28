#!/bin/bash
set -e

# Set up nginx directories
mkdir -p /var/log/nginx
chown -R www-data:www-data /var/log/nginx
chown -R www-data:www-data /app/static
chown -R www-data:www-data /app/json_data

# Debug: Check if static files exist
echo "Checking static files..."
ls -la /app/static

echo "Starting text analysis..."
# Run the text analysis script
python3 main.py --pdf_dir /app/txt_data --output_dir /app/json_data

# Wait for Flask to start
echo "Waiting for Flask to start..."
sleep 5

# Debug: Check nginx config
echo "Testing nginx configuration..."
nginx -t

echo "Starting web server..."
nginx -g "daemon off;"
echo "Tailing nginx logs..."
tail -f /var/log/nginx/error.log /var/log/nginx/access.log 