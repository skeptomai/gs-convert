# AWS Deployment Guide - Manual Setup

This guide walks you through deploying the gs-convert Web UI on AWS EC2 with CloudFront CDN.

**Target Architecture:** EC2 t4g.micro (ARM) + CloudFront + Elastic IP
**Estimated Cost:** ~$10-15/month
**Time Required:** 30-45 minutes

---

## ⚠️ Security Notice

**SSH Key Files:**
- The AWS Console will generate a `.pem` file during EC2 setup
- **Store this file securely on your local machine**
- **NEVER commit `.pem` files to git repositories**
- The `.gitignore` file already excludes `*.pem` files

**AWS Credentials:**
- Never hardcode AWS credentials in scripts or config files
- Use AWS IAM roles when possible
- Configure AWS CLI locally: `aws configure` (stores credentials in `~/.aws/` outside this repo)

---

## Prerequisites

- AWS account
- Domain name (optional but recommended)
- SSH client
- AWS CLI installed (optional, for automation scripts)

---

## Part 1: Launch EC2 Instance

### Step 1: Sign in to AWS Console

1. Go to https://console.aws.amazon.com/
2. Navigate to **EC2** service
3. Click **Launch Instance**

### Step 2: Configure Instance

**Name and Tags:**
- Name: `gs-convert-web`

**Application and OS Images (Amazon Machine Image):**
- Click **Browse more AMIs**
- Search: `ubuntu 22.04 arm64`
- Select: **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type - 64-bit (Arm)**
- AMI ID will be something like: `ami-xxxxxxxxx` (varies by region)

**Instance Type:**
- Family: **t4g** (AWS Graviton2 - ARM-based)
- Size: **t4g.micro** (1 GB RAM, 2 vCPUs)
- ✅ Free tier eligible (if within first 12 months)

**Key Pair (login):**
- Click **Create new key pair**
- Name: `gs-convert-key`
- Key pair type: **RSA**
- Private key format: **.pem** (for Mac/Linux) or **.ppk** (for Windows PuTTY)
- Click **Create key pair**
- **Save the downloaded .pem file** - you'll need this to SSH in

**Network Settings:**
- Click **Edit**
- Auto-assign public IP: **Enable**
- Firewall (security groups): **Create security group**
  - Security group name: `gs-convert-web-sg`
  - Description: `Allow HTTP, HTTPS, and SSH`

**Security group rules:**

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access (use your IP) |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS traffic |

**Configure Storage:**
- Root volume: **20 GB gp3** (General Purpose SSD)
- Delete on termination: **Yes** (default)

**Advanced Details:**
- Leave defaults

### Step 3: Launch Instance

1. Review settings in right sidebar
2. Click **Launch instance**
3. Wait 2-3 minutes for instance to start
4. Note down the **Public IPv4 address**

### Step 4: Allocate Elastic IP

An Elastic IP gives you a permanent public IP address that survives instance restarts.

1. In EC2 console, go to **Network & Security** → **Elastic IPs**
2. Click **Allocate Elastic IP address**
3. Network Border Group: Use default
4. Click **Allocate**
5. Select the new Elastic IP
6. Click **Actions** → **Associate Elastic IP address**
7. Instance: Select `gs-convert-web`
8. Click **Associate**
9. **Note down the Elastic IP** - this is your permanent public IP

---

## Part 2: Initial Server Setup

### Step 1: SSH into Server

```bash
# Set correct permissions on key file
chmod 400 ~/Downloads/gs-convert-key.pem

# SSH into instance (replace with your Elastic IP)
ssh -i ~/Downloads/gs-convert-key.pem ubuntu@YOUR_ELASTIC_IP

# Example:
# ssh -i ~/Downloads/gs-convert-key.pem ubuntu@54.123.45.67
```

You should see the Ubuntu welcome message.

### Step 2: Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

### Step 3: Configure Firewall (UFW)

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

You should see:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## Part 3: Deploy Application

### Step 1: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/skeptomai/gs-convert.git
cd gs-convert
```

### Step 2: Set Up Python Environment

```bash
# Run development setup script
./dev-setup.sh

# When prompted "Install Web UI dependencies? (y/n)", type: y

# Activate virtual environment
source .venv/bin/activate

# Install production WSGI server
pip install gunicorn
```

### Step 3: Test Application

```bash
# Test that the app runs
python -m gs_convert_ui.app

# You should see:
# * Running on http://0.0.0.0:5001
# Press Ctrl+C to stop
```

Press **Ctrl+C** to stop the test server.

### Step 4: Create Systemd Service

Create a systemd service to run the app automatically.

```bash
# Create service file
sudo nano /etc/systemd/system/gs-convert.service
```

Paste this content (replace `/home/ubuntu` if your username differs):

```ini
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
```

Save and exit (Ctrl+X, Y, Enter in nano).

### Step 5: Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/gs-convert
sudo chown ubuntu:ubuntu /var/log/gs-convert
```

### Step 6: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable gs-convert

# Start service
sudo systemctl start gs-convert

# Check status
sudo systemctl status gs-convert
```

You should see `active (running)` in green.

### Step 7: Test Local Access

```bash
# Test that the app is responding
curl http://127.0.0.1:5001

# You should see HTML output (the index page)
```

---

## Part 4: Configure Nginx Reverse Proxy

### Step 1: Create Nginx Configuration

```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Create new configuration
sudo nano /etc/nginx/sites-available/gs-convert
```

Paste this content:

```nginx
server {
    listen 80;
    server_name _;  # Accept any hostname for now

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase upload size limit (for large images)
    client_max_body_size 20M;

    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for image conversion
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Optional: Serve static files directly from Nginx (faster)
    location /static/ {
        alias /home/ubuntu/gs-convert/gs_convert_ui/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Save and exit.

### Step 2: Enable Site and Test Configuration

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/gs-convert /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# You should see:
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### Step 3: Test External Access

Open your browser and navigate to:
```
http://YOUR_ELASTIC_IP
```

You should see the gs-convert Web UI! 🎉

**Note:** You're accessing via HTTP (not HTTPS) at this point. We'll add SSL in the next section.

---

## Part 5: Set Up Domain and SSL (Optional but Recommended)

### Step 1: Point Domain to Elastic IP

In your domain registrar's DNS settings:

1. Create an **A record**:
   - Name: `@` (or `gs-convert` for subdomain)
   - Type: `A`
   - Value: `YOUR_ELASTIC_IP`
   - TTL: `3600` (or default)

2. Wait 5-10 minutes for DNS propagation
3. Test: `ping your-domain.com` should resolve to your Elastic IP

### Step 2: Update Nginx Configuration for Domain

```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/gs-convert
```

Change the `server_name` line:
```nginx
server_name your-domain.com;  # Replace with your actual domain
```

Save and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Install SSL Certificate with Let's Encrypt

```bash
# Run certbot (replace with your domain and email)
sudo certbot --nginx -d your-domain.com

# Follow prompts:
# - Enter email address
# - Agree to terms (Y)
# - Share email with EFF (optional)
# - Redirect HTTP to HTTPS? (2 = Yes, recommended)
```

Certbot will automatically:
- Obtain SSL certificate
- Update Nginx configuration
- Set up auto-renewal

### Step 4: Test HTTPS Access

Open your browser:
```
https://your-domain.com
```

You should see:
- 🔒 Padlock icon (secure connection)
- gs-convert Web UI loads

### Step 5: Verify Auto-Renewal

```bash
# Test certificate renewal (dry run)
sudo certbot renew --dry-run

# Should see: "Congratulations, all simulated renewals succeeded"
```

Certbot automatically adds a renewal cron job. Certificates renew automatically every 90 days.

---

## Part 6: Set Up CloudFront CDN (Optional - Recommended for Global Users)

CloudFront distributes your static assets (HTML/CSS/JS/images) globally for faster load times.

### Step 1: Create CloudFront Distribution

1. Go to **CloudFront** in AWS Console
2. Click **Create distribution**

**Origin Settings:**
- Origin domain: `your-domain.com` (or your Elastic IP)
- Protocol: **HTTPS only** (if you set up SSL) or **HTTP only**
- Name: Auto-filled (leave as-is)

**Default Cache Behavior:**
- Viewer protocol policy: **Redirect HTTP to HTTPS**
- Allowed HTTP methods: **GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE**
- Cache policy: **CachingDisabled** (for dynamic API routes)
- Origin request policy: **AllViewer**

**Settings:**
- Price class: **Use all edge locations** (best performance)
- Alternate domain name (CNAME): `your-domain.com` (if using custom domain)
- Custom SSL certificate: **Request certificate** (via ACM) or use existing
- Default root object: `index.html` (leave blank for Flask to handle)

3. Click **Create distribution**
4. Wait 10-15 minutes for deployment (Status: **Deployed**)

### Step 2: Request ACM Certificate (if using custom domain)

1. In CloudFront creation, click **Request certificate**
2. Domain name: `your-domain.com`
3. Validation method: **DNS validation**
4. Click **Request**
5. Add the provided CNAME record to your DNS
6. Wait for validation (usually 5-10 minutes)
7. Return to CloudFront and select the new certificate

### Step 3: Update DNS to Point to CloudFront

1. Note the **Distribution domain name** (e.g., `d1234abcd.cloudfront.net`)
2. In your DNS settings, **change the A record to a CNAME**:
   - Type: `CNAME`
   - Name: `@` or subdomain
   - Value: `d1234abcd.cloudfront.net` (your CloudFront domain)
   - TTL: `3600`

3. Wait 5-10 minutes for DNS propagation
4. Test: `https://your-domain.com` should now go through CloudFront

### Step 4: Configure Cache Behaviors for Static Assets

To cache static files efficiently:

1. In CloudFront distribution, go to **Behaviors** tab
2. Click **Create behavior**

**Path pattern:** `/static/*`
- Cache policy: **CachingOptimized**
- Origin request policy: **CORS-S3Origin**
- Compress objects automatically: **Yes**

3. Click **Create behavior**
4. Repeat for other static paths if needed

### Step 5: Update Nginx for CloudFront

Add this to your Nginx config to handle CloudFront headers:

```bash
sudo nano /etc/nginx/sites-available/gs-convert
```

Add inside the `server` block:

```nginx
    # Handle CloudFront forwarded protocol
    if ($http_cloudfront_forwarded_proto = 'https') {
        set $fe_https 'on';
    }
```

Reload Nginx:
```bash
sudo systemctl reload nginx
```

---

## Part 7: Set Up File Cleanup

Prevent disk space issues by automatically deleting old uploaded/converted files.

### Step 1: Create Cleanup Script

```bash
# Create script
sudo nano /usr/local/bin/gs-convert-cleanup.sh
```

Paste:

```bash
#!/bin/bash
# Clean up gs-convert temporary files older than 1 hour

UPLOAD_DIR="/home/ubuntu/gs-convert/gs_convert_ui/uploads"

if [ -d "$UPLOAD_DIR" ]; then
    find "$UPLOAD_DIR" -type f -mmin +60 -delete
    find "$UPLOAD_DIR" -type d -empty -delete
    echo "$(date): Cleaned up files older than 1 hour"
fi
```

Save and make executable:

```bash
sudo chmod +x /usr/local/bin/gs-convert-cleanup.sh
```

### Step 2: Add Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * /usr/local/bin/gs-convert-cleanup.sh >> /var/log/gs-convert/cleanup.log 2>&1
```

Save and exit.

### Step 3: Test Cleanup Script

```bash
# Run manually to test
/usr/local/bin/gs-convert-cleanup.sh

# Check log
cat /var/log/gs-convert/cleanup.log
```

---

## Part 8: Monitoring and Maintenance

### View Application Logs

```bash
# View real-time logs
sudo journalctl -u gs-convert -f

# View recent logs
sudo journalctl -u gs-convert -n 100

# View access logs
tail -f /var/log/gs-convert/access.log

# View error logs
tail -f /var/log/gs-convert/error.log
```

### Check Service Status

```bash
# Check if service is running
sudo systemctl status gs-convert

# Restart service if needed
sudo systemctl restart gs-convert
```

### Check Disk Space

```bash
# Check disk usage
df -h

# Check specific directory
du -sh /home/ubuntu/gs-convert/gs_convert_ui/uploads/
```

### Update Application

```bash
# SSH into server
ssh -i ~/Downloads/gs-convert-key.pem ubuntu@YOUR_ELASTIC_IP

# Navigate to app directory
cd ~/gs-convert

# Pull latest changes
git pull

# Activate environment
source .venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart gs-convert

# Check status
sudo systemctl status gs-convert
```

### Monitor CloudWatch Metrics (AWS Console)

1. Go to **CloudWatch** in AWS Console
2. Click **Metrics** → **EC2**
3. View metrics for your instance:
   - CPUUtilization
   - NetworkIn/NetworkOut
   - DiskReadBytes/DiskWriteBytes

Set up alarms if CPU > 80% for extended periods.

---

## Part 9: Security Best Practices

### Keep System Updated

```bash
# Weekly update routine
sudo apt update && sudo apt upgrade -y
sudo systemctl restart gs-convert  # If Python packages updated
sudo systemctl restart nginx       # If Nginx updated
```

### Restrict SSH Access

After initial setup, restrict SSH to your IP only:

1. Go to EC2 → Security Groups → `gs-convert-web-sg`
2. Edit inbound rule for SSH (port 22)
3. Source: **My IP** instead of `0.0.0.0/0`

### Enable AWS CloudWatch Logs (Optional)

Send application logs to CloudWatch for centralized monitoring:

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/arm64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure agent to send logs
# (Follow AWS documentation for detailed setup)
```

### Use AWS Systems Manager Session Manager (Optional)

For SSH without opening port 22:

1. Attach IAM role with `AmazonSSMManagedInstanceCore` policy to EC2 instance
2. Use Session Manager in AWS Console to connect
3. Remove SSH inbound rule from security group

---

## Part 10: Cost Optimization

### Enable Detailed Billing

1. Go to **Billing Dashboard** in AWS Console
2. Enable **Cost Explorer**
3. Set up **Budget alerts** for $20/month

### Use Reserved Instances (After 1 month)

If you plan to run for 1+ years:

1. Go to **EC2** → **Reserved Instances**
2. Purchase 1-year reservation for t4g.micro
3. Save ~30% ($6.13/month vs $8.40/month)

### Monitor Data Transfer

CloudFront data transfer is your main variable cost:
- First 1 TB/month: Free (for 12 months)
- After free tier: ~$0.085/GB

Keep an eye on CloudFront metrics in CloudWatch.

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
sudo journalctl -u gs-convert -n 50

# Common issues:
# - Port 5001 already in use: Change port in systemd service
# - Python path wrong: Check WorkingDirectory and Environment in service file
# - Permissions: Ensure ubuntu user owns /home/ubuntu/gs-convert
```

### Nginx 502 Bad Gateway

```bash
# Check if Flask app is running
sudo systemctl status gs-convert

# Check if port 5001 is listening
sudo netstat -tlnp | grep 5001

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Static Files Not Loading (CSS/JS)

**Symptoms:** Page loads but no styling, drag-and-drop doesn't work, browser console shows 403 errors for static files

**Cause:** Nginx (www-data user) can't access `/home/ubuntu/` directory

**Fix:**
```bash
# Add www-data to ubuntu group
sudo usermod -a -G ubuntu www-data

# Make home directory group-readable
sudo chmod 755 /home/ubuntu

# Restart Nginx
sudo systemctl restart nginx

# Verify static files are now accessible
curl -I http://localhost/static/js/app.js
# Should see: HTTP/1.1 200 OK
```

**Check Nginx error log for permission errors:**
```bash
sudo tail -20 /var/log/nginx/error.log
# Look for: "Permission denied" errors when accessing /home/ubuntu/gs-convert/gs_convert_ui/static/
```

### Can't Connect via HTTPS

```bash
# Check if port 443 is open in security group
# Check if SSL certificate is valid
sudo certbot certificates

# Check Nginx is listening on 443
sudo netstat -tlnp | grep 443
```

### High CPU Usage

```bash
# Check CPU usage
top

# If gs-convert is using high CPU:
# - Increase Gunicorn workers (but not more than 2x CPU cores)
# - Upgrade to t4g.small (2 GB RAM, $16/month)
# - Add CloudFront to cache static assets
```

### Disk Space Full

```bash
# Check disk usage
df -h

# If /home/ubuntu/gs-convert/gs_convert_ui/uploads/ is large:
# - Verify cleanup cron job is running
# - Manually clean up: find uploads/ -type f -mmin +60 -delete
# - Reduce retention time in cleanup script (e.g., 30 minutes instead of 60)
```

---

## Quick Reference Commands

```bash
# SSH into server
ssh -i ~/Downloads/gs-convert-key.pem ubuntu@YOUR_ELASTIC_IP

# Check service status
sudo systemctl status gs-convert
sudo systemctl status nginx

# Restart services
sudo systemctl restart gs-convert
sudo systemctl restart nginx

# View logs
sudo journalctl -u gs-convert -f
tail -f /var/log/gs-convert/access.log
tail -f /var/log/nginx/error.log

# Update application
cd ~/gs-convert && git pull && sudo systemctl restart gs-convert

# Check disk space
df -h
du -sh ~/gs-convert/gs_convert_ui/uploads/

# Manual cleanup
find ~/gs-convert/gs_convert_ui/uploads/ -type f -mmin +60 -delete
```

---

## Next Steps

1. **Test the deployment** - Upload and convert a few images
2. **Set up monitoring** - CloudWatch alarms for CPU/disk
3. **Share with community** - Post to r/apple2, Apple II forums
4. **Gather feedback** - Improve based on user reports
5. **Monitor costs** - Check AWS billing dashboard weekly

---

## Additional Resources

- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **Let's Encrypt Documentation**: https://letsencrypt.org/docs/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Flask Production Best Practices**: https://flask.palletsprojects.com/en/stable/deploying/

---

**Congratulations!** Your gs-convert Web UI is now live and accessible to the world! 🎉

*Last updated: 2025-12-10*
