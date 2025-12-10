#!/bin/bash
# Deploy gs-convert application to EC2 instance
# Usage: ./deploy-app.sh <elastic-ip> <path-to-key.pem>

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <elastic-ip> <path-to-key.pem>"
    echo "Example: $0 54.123.45.67 gs-convert-key.pem"
    exit 1
fi

ELASTIC_IP=$1
KEY_FILE=$2

if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file not found: $KEY_FILE"
    exit 1
fi

echo "🚀 Deploying gs-convert to $ELASTIC_IP..."

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@"$ELASTIC_IP" "echo '✅ SSH connection successful'" 2>/dev/null; then
    echo "❌ Cannot connect to $ELASTIC_IP"
    echo "   Make sure the instance is running and security group allows SSH from your IP"
    exit 1
fi

# Create deployment script that will run on the server
DEPLOY_SCRIPT=$(cat <<'REMOTE_SCRIPT'
#!/bin/bash
set -e

echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx

echo "📂 Cloning repository..."
cd ~
if [ -d "gs-convert" ]; then
    echo "⚠️  Repository already exists, pulling latest..."
    cd gs-convert
    git pull
else
    git clone https://github.com/skeptomai/gs-convert.git
    cd gs-convert
fi

echo "🐍 Setting up Python environment..."
./dev-setup.sh <<< "y"

echo "🔧 Activating environment and installing Gunicorn..."
source .venv/bin/activate
pip install gunicorn

echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/gs-convert.service > /dev/null <<'EOF'
[Unit]
Description=GS-Convert Web UI
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/gs-convert
Environment="PATH=/home/ubuntu/gs-convert/.venv/bin"
ExecStart=/home/ubuntu/gs-convert/.venv/bin/gunicorn \
    --bind 127.0.0.1:5001 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/gs-convert/access.log \
    --error-logfile /var/log/gs-convert/error.log \
    gs_convert_ui.app:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "📁 Creating log directory..."
sudo mkdir -p /var/log/gs-convert
sudo chown ubuntu:ubuntu /var/log/gs-convert

echo "🔄 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable gs-convert
sudo systemctl start gs-convert

echo "⏳ Waiting for service to start..."
sleep 3

if sudo systemctl is-active --quiet gs-convert; then
    echo "✅ Service started successfully"
else
    echo "❌ Service failed to start"
    sudo journalctl -u gs-convert -n 20
    exit 1
fi

echo "🌐 Configuring Nginx..."
sudo rm -f /etc/nginx/sites-enabled/default

sudo tee /etc/nginx/sites-available/gs-convert > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase upload size limit
    client_max_body_size 20M;

    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Serve static files directly
    location /static/ {
        alias /home/ubuntu/gs-convert/gs_convert_ui/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/gs-convert /etc/nginx/sites-enabled/

echo "✅ Testing Nginx configuration..."
sudo nginx -t

echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

echo "🔥 Configuring firewall..."
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

echo "🧹 Setting up file cleanup..."
sudo tee /usr/local/bin/gs-convert-cleanup.sh > /dev/null <<'EOF'
#!/bin/bash
UPLOAD_DIR="/home/ubuntu/gs-convert/gs_convert_ui/uploads"
if [ -d "$UPLOAD_DIR" ]; then
    find "$UPLOAD_DIR" -type f -mmin +60 -delete
    find "$UPLOAD_DIR" -type d -empty -delete
    echo "$(date): Cleaned up files older than 1 hour"
fi
EOF

sudo chmod +x /usr/local/bin/gs-convert-cleanup.sh

# Add cron job if not exists
(crontab -l 2>/dev/null | grep -q gs-convert-cleanup) || (crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/gs-convert-cleanup.sh >> /var/log/gs-convert/cleanup.log 2>&1") | crontab -

echo "✅ Deployment complete!"
REMOTE_SCRIPT
)

# Execute deployment script on remote server
echo "📤 Uploading and executing deployment script..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ubuntu@"$ELASTIC_IP" "bash -s" <<< "$DEPLOY_SCRIPT"

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
if curl -s -o /dev/null -w "%{http_code}" "http://${ELASTIC_IP}" | grep -q "200"; then
    echo "✅ Application is responding!"
else
    echo "⚠️  Application might not be responding yet, check logs:"
    echo "   ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
    echo "   sudo journalctl -u gs-convert -f"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Application URL: http://${ELASTIC_IP}"
echo ""
echo "Next steps:"
echo "  1. Test the application in your browser"
echo "  2. Set up a domain and SSL:"
echo "     ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
echo "     sudo certbot --nginx -d your-domain.com"
echo ""
echo "  3. Monitor logs:"
echo "     ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
echo "     sudo journalctl -u gs-convert -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
