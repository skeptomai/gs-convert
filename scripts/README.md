# Deployment Scripts

Automated scripts for deploying gs-convert Web UI to AWS EC2.

## ⚠️ Security Warning

**NEVER commit AWS credentials to this repository!**

These scripts use the AWS CLI which reads credentials from:
- `~/.aws/credentials` (AWS CLI configuration)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (if running on EC2)

**All credential files are already in `.gitignore`:**
- `*.pem` (SSH keys)
- `.aws-instance-info` (instance details)
- `gs-convert-key.*` (generated keys)

**If you fork this repository:**
1. ✅ Configure AWS CLI locally: `aws configure`
2. ✅ Run scripts from your local machine
3. ✅ Generated keys stay local (ignored by git)
4. ❌ NEVER add credentials to scripts
5. ❌ NEVER commit `.pem` files
6. ❌ NEVER hardcode AWS keys

## Prerequisites

- **AWS CLI** installed and configured (`aws configure`)
- **SSH client** (built-in on Mac/Linux)
- **AWS credentials** with permissions to create EC2 instances, security groups, and Elastic IPs
  - **Note:** Configure via `aws configure` - credentials are stored in `~/.aws/credentials` (outside this repo)

## Quick Start

### 1. Provision EC2 Instance

This creates a new t4g.micro ARM instance with all required AWS resources:

```bash
cd scripts
chmod +x *.sh
./provision-ec2.sh
```

This will:
- ✅ Find latest Ubuntu 22.04 ARM64 AMI
- ✅ Create SSH key pair (`gs-convert-key.pem`)
- ✅ Create security group with ports 22, 80, 443 open
- ✅ Launch t4g.micro instance
- ✅ Allocate and associate Elastic IP
- ✅ Save instance info to `.aws-instance-info`

**Output:** Elastic IP address and SSH command

### 2. Deploy Application

This installs and configures the application on the instance:

```bash
./deploy-app.sh <elastic-ip> gs-convert-key.pem

# Example:
./deploy-app.sh 54.123.45.67 gs-convert-key.pem
```

This will:
- ✅ Install system dependencies (Python, Nginx, Certbot)
- ✅ Clone gs-convert repository
- ✅ Set up Python virtual environment
- ✅ Create systemd service for Gunicorn
- ✅ Configure Nginx reverse proxy
- ✅ Set up firewall (UFW)
- ✅ Create file cleanup cron job
- ✅ Start all services

**Output:** Application URL (http://your-elastic-ip)

### 3. Update Application (Future Updates)

When you push changes to GitHub, update the running instance:

```bash
./update-app.sh <elastic-ip> gs-convert-key.pem

# Example:
./update-app.sh 54.123.45.67 gs-convert-key.pem
```

This will:
- ✅ Pull latest code from GitHub
- ✅ Update Python dependencies
- ✅ Restart application service
- ✅ Verify service is running

---

## Script Details

### provision-ec2.sh

**Purpose:** Automates AWS infrastructure provisioning

**What it creates:**
- EC2 t4g.micro instance (ARM64)
- Security group with SSH, HTTP, HTTPS access
- SSH key pair for authentication
- Elastic IP for permanent address

**Environment variables:**
- `AWS_DEFAULT_REGION` - AWS region (default: us-east-1)

**Output files:**
- `gs-convert-key.pem` - SSH private key (chmod 400)
- `.aws-instance-info` - Instance details for reference

**Cost:** ~$8-12/month

### deploy-app.sh

**Purpose:** Deploys application to existing EC2 instance

**What it installs:**
- Python 3.10+ with pip and venv
- Git (for cloning repository)
- Nginx (web server)
- Certbot (SSL certificates)
- Gunicorn (WSGI server)

**What it configures:**
- Systemd service for automatic startup
- Nginx reverse proxy on port 80
- UFW firewall rules
- Log rotation and cleanup
- Hourly cleanup cron job

**Services created:**
- `gs-convert.service` - Main application
- `nginx.service` - Web server

**Logs:**
- `/var/log/gs-convert/access.log` - HTTP access logs
- `/var/log/gs-convert/error.log` - Application errors
- `/var/log/gs-convert/cleanup.log` - File cleanup logs

### update-app.sh

**Purpose:** Updates running application with latest code

**What it does:**
- Pulls latest changes from GitHub main branch
- Updates Python dependencies if changed
- Restarts application service
- Verifies service health

**Downtime:** ~3-5 seconds during restart

**Rollback:** If update fails, SSH in and run:
```bash
cd ~/gs-convert
git checkout <previous-commit>
sudo systemctl restart gs-convert
```

---

## Manual Operations

### SSH into Instance

```bash
ssh -i gs-convert-key.pem ubuntu@<elastic-ip>
```

### View Logs

```bash
# Real-time application logs
sudo journalctl -u gs-convert -f

# Recent errors
sudo journalctl -u gs-convert -n 100 --no-pager

# Access logs
tail -f /var/log/gs-convert/access.log

# Error logs
tail -f /var/log/gs-convert/error.log
```

### Check Service Status

```bash
sudo systemctl status gs-convert
sudo systemctl status nginx
```

### Restart Services

```bash
sudo systemctl restart gs-convert
sudo systemctl restart nginx
```

### Manual Cleanup

```bash
# Clean up old uploads (files older than 1 hour)
find ~/gs-convert/gs_convert_ui/uploads/ -type f -mmin +60 -delete

# Check disk space
df -h
du -sh ~/gs-convert/gs_convert_ui/uploads/
```

---

## Setting Up SSL (After Initial Deployment)

### 1. Point Domain to Elastic IP

In your DNS provider:
- Create A record: `your-domain.com` → `<elastic-ip>`
- Wait 5-10 minutes for propagation

### 2. Run Certbot

```bash
# SSH into instance
ssh -i gs-convert-key.pem ubuntu@<elastic-ip>

# Run certbot
sudo certbot --nginx -d your-domain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Redirect HTTP to HTTPS? Yes
```

Certbot will:
- Obtain free SSL certificate from Let's Encrypt
- Update Nginx configuration automatically
- Set up auto-renewal cron job

### 3. Verify HTTPS

Visit: `https://your-domain.com`

You should see 🔒 padlock icon.

---

## Adding CloudFront CDN (Optional)

For better global performance and caching:

### 1. Create CloudFront Distribution

1. AWS Console → CloudFront → Create Distribution
2. Origin domain: Your Elastic IP or domain
3. Protocol: HTTPS only (if SSL configured)
4. Allowed methods: All (GET, POST, etc.)
5. Cache policy: CachingDisabled (for API) or create custom
6. Create distribution

### 2. Request ACM Certificate (If Using Custom Domain)

1. In CloudFront creation, click "Request certificate"
2. Domain: `your-domain.com`
3. Validation: DNS
4. Add CNAME record to DNS
5. Wait for validation

### 3. Update DNS

Change your A record to CNAME pointing to CloudFront:
- Type: `CNAME`
- Name: `your-domain.com`
- Value: `d1234abcd.cloudfront.net` (your distribution)

Wait 10-15 minutes for CloudFront deployment.

---

## Troubleshooting

### Script Fails: "Cannot connect to EC2 instance"

**Cause:** SSH not ready yet or security group blocking

**Fix:**
```bash
# Wait 1-2 minutes, then retry
./deploy-app.sh <elastic-ip> gs-convert-key.pem

# Or check security group allows your IP for SSH
aws ec2 describe-security-groups --group-names gs-convert-web-sg
```

### Application Won't Start

**Check logs:**
```bash
ssh -i gs-convert-key.pem ubuntu@<elastic-ip>
sudo journalctl -u gs-convert -n 50
```

**Common issues:**
- Python virtual environment path wrong: Check `/etc/systemd/system/gs-convert.service`
- Port 5001 in use: Change port in systemd service
- Permissions: `sudo chown -R ubuntu:ubuntu ~/gs-convert`

### Nginx 502 Bad Gateway

**Check if Flask app is running:**
```bash
sudo systemctl status gs-convert
curl http://127.0.0.1:5001
```

**Fix:**
```bash
sudo systemctl restart gs-convert
sudo systemctl restart nginx
```

### High CPU Usage

**Check top:**
```bash
top
```

**Solutions:**
- Reduce Gunicorn workers in `/etc/systemd/system/gs-convert.service`
- Upgrade to t4g.small: `aws ec2 modify-instance-attribute --instance-id <id> --instance-type t4g.small`
- Add CloudFront to cache static assets

### Out of Disk Space

**Check usage:**
```bash
df -h
du -sh ~/gs-convert/gs_convert_ui/uploads/
```

**Fix:**
```bash
# Manual cleanup
find ~/gs-convert/gs_convert_ui/uploads/ -type f -mmin +60 -delete

# Check cleanup cron is running
crontab -l
tail -f /var/log/gs-convert/cleanup.log
```

### Static Files Not Loading (403 Forbidden)

**Symptoms:**
- Page loads but no styling
- Drag-and-drop doesn't work
- Browser console shows 403 errors for /static/js/app.js or /static/css/style.css

**Cause:** Nginx can't access files in /home/ubuntu/ directory

**Fix:**
```bash
# Add www-data to ubuntu group
sudo usermod -a -G ubuntu www-data

# Make home directory group-readable
sudo chmod 755 /home/ubuntu

# Restart Nginx
sudo systemctl restart nginx

# Test
curl -I http://localhost/static/js/app.js
# Should return: HTTP/1.1 200 OK
```

**Note:** The deployment script now does this automatically, but if you deployed manually or encounter this issue, use the fix above.

---

## Monitoring

### CloudWatch Metrics (AWS Console)

1. Go to CloudWatch → Metrics → EC2
2. Select instance
3. Monitor:
   - CPUUtilization (should be < 80%)
   - NetworkIn/NetworkOut
   - DiskReadBytes/DiskWriteBytes

### Set Up Alarms

1. CloudWatch → Alarms → Create Alarm
2. Metric: EC2 CPUUtilization
3. Condition: > 80% for 5 minutes
4. Action: Send SNS notification to your email

### Application Metrics

Add to your cron:
```bash
# Check disk usage daily at 9 AM
0 9 * * * df -h | grep /dev/root >> /var/log/gs-convert/disk-usage.log
```

---

## Cost Optimization

### Use Reserved Instances (After Testing)

If you plan to run for 1+ years:

```bash
# Purchase 1-year t4g.micro reservation
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id <offering-id> \
    --instance-count 1

# Savings: ~30% ($6.13/month vs $8.40/month)
```

### Monitor Costs

1. AWS Console → Billing Dashboard
2. Set up budget alerts for $20/month
3. Enable Cost Explorer

### Reduce Data Transfer Costs

- Add CloudFront (caches static assets)
- Compress images before upload (client-side)
- Clean up old files frequently

---

## Cleanup / Teardown

### Stop Instance (Temporarily)

```bash
aws ec2 stop-instances --instance-ids <instance-id>

# Cost while stopped: ~$0.50/month (EBS storage only)
```

### Terminate Instance (Permanently)

```bash
# WARNING: This deletes everything!

# Terminate instance
aws ec2 terminate-instances --instance-ids <instance-id>

# Release Elastic IP
aws ec2 release-address --allocation-id <allocation-id>

# Delete security group (wait for instance termination)
aws ec2 delete-security-group --group-id <security-group-id>

# Delete key pair
aws ec2 delete-key-pair --key-name gs-convert-key
rm gs-convert-key.pem
```

---

## Security Best Practices

### Restrict SSH Access

After initial setup, limit SSH to your IP:

```bash
# Get your current IP
MY_IP=$(curl -s https://checkip.amazonaws.com)

# Update security group
aws ec2 revoke-security-group-ingress \
    --group-name gs-convert-web-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name gs-convert-web-sg \
    --protocol tcp \
    --port 22 \
    --cidr "${MY_IP}/32"
```

### Enable Automatic Security Updates

```bash
ssh -i gs-convert-key.pem ubuntu@<elastic-ip>

sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Regular Updates

Weekly maintenance:
```bash
ssh -i gs-convert-key.pem ubuntu@<elastic-ip>

sudo apt update && sudo apt upgrade -y
sudo systemctl restart gs-convert
sudo systemctl restart nginx
```

---

## Support

For detailed manual deployment instructions, see:
- [`docs/AWS_DEPLOYMENT_GUIDE.md`](../docs/AWS_DEPLOYMENT_GUIDE.md) - Step-by-step manual setup
- [`docs/SCALING_AND_DEPLOYMENT_OPTIONS.md`](../docs/SCALING_AND_DEPLOYMENT_OPTIONS.md) - Architecture options

For issues:
- Check logs: `sudo journalctl -u gs-convert -f`
- GitHub Issues: https://github.com/skeptomai/gs-convert/issues
- AWS Support: https://console.aws.amazon.com/support/

---

*Last updated: 2025-12-10*
