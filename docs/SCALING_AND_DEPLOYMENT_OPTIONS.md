# Scaling and Deployment Options for gs-convert Web UI

This document outlines different approaches for hosting the gs-convert web UI on AWS for public consumption, with cost estimates and architectural considerations.

---

## Overview

The gs-convert web UI is a Flask-based application that converts images to Apple IIgs format. For public hosting, we need to consider:

- Uptime and reliability
- Response time (image conversion can take 2-10 seconds)
- Scaling for traffic spikes
- Cost efficiency for a niche retro computing tool
- File cleanup (temporary uploaded/converted files)

---

## Option 1: AWS Lambda + API Gateway (Serverless)

**Cost: ~$5-15/month for light-moderate usage**

### Architecture

- **AWS Lambda** for Python backend (Flask → AWS Lambda adapter)
- **API Gateway** for HTTP routing
- **S3** for static files (HTML/CSS/JS) + CloudFront CDN
- **S3** for temporary file storage (with lifecycle policies to auto-delete)

### Cost Breakdown (Light-Moderate Usage)

- **Lambda**: First 1M requests free, then $0.20/1M requests + $0.0000166667/GB-second compute
- **API Gateway**: First 1M requests free (12 months), then $1.00/1M requests
- **S3 Storage**: $0.023/GB storage + $0.09/GB transfer
- **CloudFront**: 1TB free transfer (12 months), then $0.085/GB
- **Estimated: $5-15/month for ~10,000 conversions**

### Pros

- ✅ Scales to zero (only pay for actual usage)
- ✅ No server management
- ✅ Auto-scales to handle traffic spikes
- ✅ Free tier covers light usage
- ✅ No infrastructure to maintain

### Cons

- ❌ Cold start delays (2-3 seconds for first request after idle period)
- ❌ 15-minute Lambda timeout (fine for single images, but watch batch operations)
- ❌ Requires refactoring Flask app for Lambda (use AWS Lambda adapter)
- ❌ S3 cleanup is critical (or costs balloon with abandoned files)
- ❌ More complex deployment pipeline

### Best For

- Very spiky traffic (days with zero usage, then sudden bursts)
- Cost-sensitive projects where you want to pay only for actual usage
- Projects where cold starts are acceptable (not user-facing real-time apps)

---

## Option 2: EC2 t4g.micro (ARM) - Single Instance

**Cost: ~$8-12/month**

### Architecture

- **EC2 t4g.micro** instance (ARM-based, 2 vCPU, 1GB RAM)
- Run Flask app with **Gunicorn** (4 workers) + **Nginx** reverse proxy
- Direct storage on instance (with cleanup cronjob)
- **Elastic IP** for consistent public address
- DNS points directly to Elastic IP

### Cost Breakdown

- **EC2 t4g.micro**: $0.0084/hour × 730 hours = $6.13/month (1-year reserved) or ~$8/month on-demand
- **Elastic IP**: Free while instance running, $0.005/hour if unattached
- **Data transfer**: First 100GB free, then $0.09/GB
- **Estimated: $8-12/month for light-moderate usage**

### Setup

```bash
# On EC2 t4g.micro (Ubuntu ARM64)
git clone https://github.com/skeptomai/gs-convert.git
cd gs-convert
./dev-setup.sh
source .venv/bin/activate
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 gs_convert_ui.app:app

# Set up Nginx reverse proxy + SSL (Let's Encrypt)
sudo apt install nginx certbot python3-certbot-nginx
# Configure Nginx to proxy to port 5001
# Set up certbot for SSL
```

### Pros

- ✅ Simple deployment (just run your Flask app)
- ✅ No cold starts - always fast
- ✅ Can handle batch operations easily
- ✅ Easy to SSH in and debug
- ✅ Free tier eligible (750 hours/month for 12 months = essentially free first year)
- ✅ ARM instance is perfect since developed on Apple Silicon
- ✅ Can handle ~50-100 concurrent users on t4g.micro

### Cons

- ❌ Must handle scaling manually (upgrade instance type or add more instances)
- ❌ You manage security updates
- ❌ Not auto-scaling (but can upgrade to larger instance types: t4g.small, t4g.medium)
- ❌ Single point of failure (no redundancy)
- ❌ Manual DNS management

### Best For

- Starting out with predictable, low traffic
- Projects where you want full control and SSH access
- When consistent response time matters (no cold starts)
- First 12 months with AWS (free tier)

### Scaling Path

When traffic grows, manually upgrade to:
1. Larger instance type (t4g.small: $16/month, t4g.medium: $33/month)
2. Add Application Load Balancer + multiple instances (see Option 2B)

---

## Option 2B: EC2 + Application Load Balancer (ALB)

**Cost: ~$25-30/month**

### Architecture

- **1-2 EC2 t4g.micro** instances in Auto Scaling Group
- **Application Load Balancer** in front
- ALB handles SSL (free AWS Certificate Manager certificate)
- DNS points to ALB
- Auto Scaling based on CPU/memory/request count

### Cost Breakdown

- **1x EC2 t4g.micro**: ~$8/month
- **ALB**: $16.20/month (fixed) + $0.008/LCU-hour (~$0.50-2/month for light traffic)
- **Data transfer**: First 100GB free, then $0.09/GB
- **Total: ~$25-30/month**

### Pros

- ✅ Can auto-scale (1-10 instances based on load)
- ✅ Health checks and auto-replacement of unhealthy instances
- ✅ Zero-downtime deployments (deploy new version, ALB drains old connections)
- ✅ Production-grade HA setup
- ✅ SSL/TLS termination at load balancer
- ✅ Distributes load across multiple AZs (availability zones)

### Cons

- ❌ $16/month ALB cost even with just 1 instance
- ❌ More complex setup (Auto Scaling Groups, Target Groups, health checks)
- ❌ Overkill for low-traffic hobby projects

### Best For

- Production applications expecting significant traffic
- When you want hands-off auto-scaling
- When high availability is important
- When $25/month operational simplicity is worth it

---

## Option 2C: EC2 + CloudFront (CDN)

**Cost: ~$10-15/month**

### Architecture

- **EC2 t4g.micro** with Elastic IP
- **CloudFront CDN** in front (caches static assets, proxies API requests to EC2)
- CloudFront handles SSL (free ACM certificate)
- DNS points to CloudFront distribution
- Static files (HTML/CSS/JS/images) cached at edge locations globally

### Cost Breakdown

- **EC2 t4g.micro**: ~$8/month
- **CloudFront**: First 1TB transfer free (12 months), then ~$0.085/GB
- Reduces EC2 bandwidth costs by caching static content
- **Total: ~$10-15/month**

### Pros

- ✅ Global CDN speeds up static content delivery
- ✅ Reduces load on EC2 (static assets served from edge)
- ✅ DDoS protection included with CloudFront
- ✅ Free SSL certificate via ACM
- ✅ Can manually add more EC2 instances later behind CloudFront
- ✅ Improves performance for international users

### Cons

- ❌ Still manual scaling (but CDN helps reduce load significantly)
- ❌ More DNS/networking configuration
- ❌ Cache invalidation required when updating static files

### Best For

- Public-facing applications with global users
- When you want performance improvement without ALB cost
- Projects expecting international traffic
- Good middle ground between bare EC2 and full ALB setup

### Scaling Path

When traffic grows:
1. Add more EC2 instances manually
2. Later: Insert ALB between CloudFront and EC2 instances for true auto-scaling

---

## Option 3: AWS Lightsail (Container Service)

**Cost: ~$10-20/month flat rate**

### Architecture

- **Lightsail Container Service** (easiest AWS option)
- Docker container with Flask app + Gunicorn
- Built-in load balancer
- Managed SSL certificate (Let's Encrypt)
- Simple deployment via Docker image push

### Cost Breakdown

- **Lightsail Container (Micro)**: $10/month for 0.25 vCPU, 512 MB RAM, 500GB transfer
- **Lightsail Container (Small)**: $20/month for 0.5 vCPU, 1 GB RAM, 1TB transfer
- **Lightsail Container (Medium)**: $40/month for 1 vCPU, 2 GB RAM, 2TB transfer
- **SSL certificate**: Free (auto-provisioned Let's Encrypt)
- **Predictable flat rate pricing**

### Setup

```bash
# Create Dockerfile
# Build and push to Lightsail
aws lightsail push-container-image --service-name gs-convert --label flask-app --image gs-convert:latest

# Deploy container
aws lightsail create-container-service-deployment \
  --service-name gs-convert \
  --containers file://containers.json \
  --public-endpoint file://public-endpoint.json
```

### Pros

- ✅ Simplest AWS deployment (easier than EC2)
- ✅ Predictable flat-rate pricing (no surprise bills)
- ✅ Auto-SSL with Let's Encrypt
- ✅ Easy container deployments (push Docker image)
- ✅ Built-in load balancing across container instances
- ✅ No need to manage OS updates (container-based)
- ✅ Can scale by upgrading plan or adding more container nodes

### Cons

- ❌ Less flexible than EC2/Lambda
- ❌ Fixed capacity (but can scale service size)
- ❌ Still requires creating Docker container image
- ❌ Less control over underlying infrastructure

### Best For

- Developers comfortable with Docker
- Projects wanting predictable costs
- "Set it and forget it" deployments
- When you want managed infrastructure without complexity

---

## Comparison Table

| Option | Monthly Cost | Scaling | Complexity | Best For |
|--------|-------------|---------|------------|----------|
| **Lambda + API Gateway** | $5-15 | Auto (infinite) | High | Spiky traffic, pay-per-use |
| **EC2 t4g.micro** | $8-12 | Manual | Low | Starting out, full control |
| **EC2 + ALB** | $25-30 | Auto | Medium | Production HA |
| **EC2 + CloudFront** | $10-15 | Manual | Medium | Global users, CDN benefits |
| **Lightsail Container** | $10-20 | Manual | Low-Medium | Docker users, predictable costs |

---

## Recommended Approach: EC2 + CloudFront (Option 2C)

### Why This Is the Best Starting Point

1. **Only $2-5 more than bare EC2** (~$10-15/month vs $8-12/month)
2. **CloudFront offloads static files** (HTML/CSS/JS/preview images)
3. **Better global performance** (edge locations worldwide)
4. **DDoS protection included** (CloudFront shields your origin)
5. **Free SSL certificate** via AWS Certificate Manager
6. **Can still manually scale EC2 when needed** (upgrade instance type)
7. **Future path**: Add ALB between CloudFront and multiple EC2 instances

### When to Consider Alternatives

**Choose Lambda (Option 1) if:**
- Traffic is extremely spiky (viral Reddit posts, then weeks of silence)
- You want absolute minimum cost
- You're comfortable with cold starts

**Choose bare EC2 (Option 2) if:**
- You want the absolute simplest setup
- You're in AWS free tier (first 12 months)
- Traffic is US-only and low-volume

**Choose EC2 + ALB (Option 2B) if:**
- You're getting >100 concurrent users consistently
- You want true auto-scaling and HA
- $25/month seems worth the operational simplicity
- This is a production service, not a hobby project

**Choose Lightsail (Option 3) if:**
- You love Docker and container workflows
- You want predictable billing
- You prefer managed services over DIY EC2

---

## Cost Comparison for 10,000 Conversions/Month

Assuming average 2MB upload + 32KB .3200 output + 50KB preview per conversion:

| Option | Compute | Transfer | Storage | **Total** |
|--------|---------|----------|---------|-----------|
| Lambda | ~$3 | ~$2 | ~$2 | **~$7** |
| EC2 t4g.micro | $8 | Included | Included | **~$8** |
| EC2 + CloudFront | $8 | $1 | Included | **~$9** |
| EC2 + ALB | $24 | Included | Included | **~$24** |
| Lightsail Small | $20 flat | Included | Included | **~$20** |

---

## When You Actually Need ALB

**Reality check for a niche retro computing tool:**

- **Option 2 (bare EC2)** is probably fine until you're getting 100+ concurrent users
- **Option 2C (EC2 + CloudFront)** is smart insurance for $2-5/month more
- **Option 2B (EC2 + ALB)** is for when you're popular enough that $25/month is trivial

A single t4g.micro can handle:
- ~50-100 concurrent users
- ~10,000-50,000 conversions/month
- ~1-2 conversions/second sustained

You'll know you need to upgrade when:
- CPU consistently >80%
- Response times degrade
- You're getting actual user complaints

---

## Deployment Quick Start (EC2 + CloudFront)

### 1. Launch EC2 Instance

```bash
# Launch t4g.micro Ubuntu ARM64
# Security group: Allow SSH (22), HTTP (80), HTTPS (443)
# Elastic IP: Allocate and associate

# SSH in
ssh -i your-key.pem ubuntu@your-elastic-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone and setup
git clone https://github.com/skeptomai/gs-convert.git
cd gs-convert
./dev-setup.sh
source .venv/bin/activate
pip install gunicorn

# Run with systemd
sudo nano /etc/systemd/system/gs-convert.service
# (Create systemd service file)

sudo systemctl enable gs-convert
sudo systemctl start gs-convert
```

### 2. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Set Up CloudFront

```bash
# Create CloudFront distribution
# Origin: Your Elastic IP or domain
# Cache behavior: Cache static assets, pass through POST requests
# SSL: Use ACM certificate for your domain

# Point DNS to CloudFront distribution domain
```

### 4. Cleanup Cronjob

```bash
# Add to crontab
0 * * * * find /path/to/gs-convert/uploads -mtime +1 -delete
```

---

## Monitoring and Maintenance

### Essential Monitoring

- **CloudWatch Metrics**: CPU, Memory, Network (free on EC2)
- **Nginx access logs**: Track requests, errors
- **Disk space**: Monitor `/tmp` or upload directory
- **Response times**: Add application-level timing logs

### Security Considerations

- Keep Ubuntu and Python packages updated
- Use AWS Security Groups (firewall rules)
- Rotate SSH keys
- Enable CloudFront access logs
- Consider AWS WAF if DDoS is a concern

### Backup Strategy

- Code: Already in GitHub
- No persistent data to back up (stateless application)
- Recreate instance from scratch in ~15 minutes if needed

---

## Future Enhancements

When traffic justifies the complexity:

1. **Add Redis caching** for frequently converted images
2. **Background job queue** (Celery + SQS) for async processing
3. **Multiple EC2 instances + ALB** for high availability
4. **RDS for persistent storage** if you add user accounts/galleries
5. **S3 for converted images** if you want to cache/share conversions

---

## Conclusion

**Start with Option 2C (EC2 t4g.micro + CloudFront)** for ~$10-15/month:
- Simple enough to deploy in an afternoon
- Fast enough for great user experience
- Scalable enough for most hobby projects
- Cheap enough to run indefinitely

Upgrade to ALB when you're successful enough that $25/month doesn't matter.

---

*Last updated: 2025-12-10*
