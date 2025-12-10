#!/bin/bash
# Update gs-convert application on running EC2 instance
# Usage: ./update-app.sh <elastic-ip> <path-to-key.pem>

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

echo "🔄 Updating gs-convert on $ELASTIC_IP..."

# Create update script
UPDATE_SCRIPT=$(cat <<'REMOTE_SCRIPT'
#!/bin/bash
set -e

cd ~/gs-convert

echo "📥 Pulling latest changes..."
git fetch origin
git pull origin main

echo "🐍 Updating dependencies..."
source .venv/bin/activate
pip install -r requirements.txt --upgrade

echo "🔄 Restarting service..."
sudo systemctl restart gs-convert

echo "⏳ Waiting for service to start..."
sleep 3

if sudo systemctl is-active --quiet gs-convert; then
    echo "✅ Service restarted successfully"
    sudo systemctl status gs-convert --no-pager
else
    echo "❌ Service failed to restart"
    sudo journalctl -u gs-convert -n 20
    exit 1
fi

echo "✅ Update complete!"
REMOTE_SCRIPT
)

# Execute update script on remote server
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ubuntu@"$ELASTIC_IP" "bash -s" <<< "$UPDATE_SCRIPT"

# Test the updated deployment
echo ""
echo "🧪 Testing updated deployment..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${ELASTIC_IP}")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Application is responding correctly (HTTP $HTTP_CODE)"
else
    echo "⚠️  Application returned HTTP $HTTP_CODE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ UPDATE SUCCESSFUL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Application URL: http://${ELASTIC_IP}"
echo ""
echo "To view logs:"
echo "  ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
echo "  sudo journalctl -u gs-convert -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
