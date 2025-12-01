# AWS Deployment Guide for Diabetes Tracker

## Recommended Services (Cheapest Options)

### 🏆 **Option 1: AWS App Runner** (Recommended)
**Best for: Low traffic, pay-per-use, minimal maintenance**

**Cost:** ~$0.007 per vCPU-hour + $0.0008 per GB-hour + data transfer
- For low traffic: **~$2-5/month**
- Scales to zero when not in use
- Automatic HTTPS, load balancing, and scaling

**Pros:**
- Very cheap for low traffic
- Automatic deployments from GitHub/ECR
- Built-in HTTPS and load balancing
- No server management
- Easy to set up

**Cons:**
- Requires containerization (Docker)
- Slightly more setup initially

---

### **Option 2: AWS Lightsail**
**Best for: Predictable pricing, simple setup**

**Cost:** **$3.50-5/month** (fixed pricing)
- $3.50/month for 512MB RAM, 1 vCPU
- $5/month for 1GB RAM, 1 vCPU

**Pros:**
- Fixed monthly cost (predictable)
- Simple setup (like a VPS)
- Can run Flask directly
- Includes static IP and DNS

**Cons:**
- Pay even when not in use
- Manual scaling
- You manage the server

---

### **Option 3: EC2 t2.micro/t3.micro**
**Best for: Full control, same instance as database, or free tier**

**Cost:** 
- **Free tier:** $0/month (first 12 months, 750 hours/month)
- **After free tier:** ~$8-10/month for t3.micro
- **t2.micro:** ~$8/month (burstable performance)
- **t3.micro:** ~$7.50/month (better performance)

**Pros:**
- Free tier available (great for first year)
- Full control over the server
- Can run app and DB on same instance (save costs)
- No Docker required (can run Flask directly)
- Familiar if you already manage EC2 for database
- Can use same security group/VPC as your database

**Cons:**
- More expensive than App Runner after free tier
- You manage everything (updates, security, monitoring)
- No automatic scaling
- Need to set up HTTPS yourself (Let's Encrypt)
- Need to configure reverse proxy (nginx) for production
- Manual deployments

---

## Deployment: AWS App Runner (Recommended)

### Prerequisites
1. AWS Account
2. Docker installed locally
3. AWS CLI configured
4. Your database already running on EC2 (with public IP or VPN)

### Step 1: Create Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (App Runner uses PORT environment variable)
ENV PORT=8000
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 'main:app'"]
```

### Step 2: Update requirements.txt

Add `gunicorn` for production:

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 3: Update main.py for Production

Modify `main.py` to work with App Runner:

```python
#!/usr/bin/env python3
"""
Main entry point for the Diabetes Tracker application.
"""

import os
from src.diabetes_tracker.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### Step 4: Create .dockerignore

Create `.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.env
.git
.gitignore
README.md
docs/
tests/
archive/
*.md
.DS_Store
```

### Step 5: Build and Push Docker Image

#### Option A: Using AWS ECR (Recommended)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name diabetes-tracker --region us-east-1

# 2. Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# 3. Build image
docker build -t diabetes-tracker .

# 4. Tag image
docker tag diabetes-tracker:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/diabetes-tracker:latest

# 5. Push image
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/diabetes-tracker:latest
```

#### Option B: Using GitHub Container Registry

```bash
# 1. Build and tag
docker build -t ghcr.io/<your-username>/diabetes-tracker:latest .

# 2. Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u <your-username> --password-stdin

# 3. Push
docker push ghcr.io/<your-username>/diabetes-tracker:latest
```

### Step 6: Configure App Runner Service

1. Go to AWS Console → App Runner
2. Click "Create service"
3. Choose "Container registry" → "Amazon ECR" (or your registry)
4. Select your image
5. Configure service:
   - **Service name:** `diabetes-tracker`
   - **Virtual CPU:** 0.25 vCPU (cheapest)
   - **Memory:** 0.5 GB (cheapest)
   - **Port:** 8000
   - **Start command:** (leave empty, handled by Dockerfile)

6. **Environment variables:**
   ```
   DB_HOST=<your-ec2-ip-or-domain>
   DB_PORT=5432
   DB_NAME=diabetes_tracker
   DB_USER=postgres
   DB_PASSWORD=<your-db-password>
   OPENAI_API_KEY=<your-openai-key>
   FLASK_ENV=production
   PORT=8000
   ```

7. **Auto-deploy:** Enable if using ECR with image push triggers

8. Create service

### Step 7: Configure Database Security

Make sure your EC2 PostgreSQL allows connections from App Runner:

1. **EC2 Security Group:**
   - Add inbound rule: PostgreSQL (5432) from App Runner's VPC
   - Or temporarily allow from 0.0.0.0/0 for testing (not recommended for production)

2. **PostgreSQL Configuration:**
   - Already configured for remote connections (based on your setup guide)

### Step 8: Access Your App

App Runner provides a URL like:
```
https://xxxxx.us-east-1.awsapprunner.com
```

---

## Deployment: AWS Lightsail (Alternative)

### Step 1: Create Lightsail Instance

1. Go to AWS Console → Lightsail
2. Create instance:
   - **Platform:** Linux/Unix
   - **Blueprint:** Python 3.11
   - **Instance plan:** $3.50/month (512MB) or $5/month (1GB)

### Step 2: Connect and Setup

```bash
# Connect via SSH (use Lightsail's browser SSH or SSH key)
ssh bitnami@<your-instance-ip>

# Install dependencies
sudo apt update
sudo apt install -y python3-pip postgresql-client

# Clone your repository
git clone <your-repo-url>
cd diabetes-tracker

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install gunicorn

# Create .env file
nano .env
# Add your environment variables
```

### Step 3: Run with Gunicorn

```bash
# Install gunicorn
pip3 install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 'main:app'
```

### Step 4: Setup as System Service

Create `/etc/systemd/system/diabetes-tracker.service`:

```ini
[Unit]
Description=Diabetes Tracker Flask App
After=network.target

[Service]
User=bitnami
WorkingDirectory=/home/bitnami/diabetes-tracker
Environment="PATH=/home/bitnami/diabetes-tracker/venv/bin"
ExecStart=/home/bitnami/diabetes-tracker/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 'main:app'
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable diabetes-tracker
sudo systemctl start diabetes-tracker
```

### Step 5: Configure Static IP and Domain

1. In Lightsail, create static IP
2. Attach to your instance
3. Configure DNS (optional)

---

## Deployment: EC2 (Full Control Option)

### When to Choose EC2

- You want to run app and database on the same instance (save costs)
- You're still in AWS free tier (first 12 months)
- You want full control over the server
- You're already familiar with EC2 management
- You want to use the same VPC/security group as your database

### Step 1: Create EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose:
   - **AMI:** Ubuntu 22.04 LTS (free tier eligible)
   - **Instance type:** t2.micro or t3.micro (free tier eligible)
   - **Key pair:** Create or select existing
   - **Security group:** 
     - Allow SSH (22) from your IP
     - Allow HTTP (80) from anywhere
     - Allow HTTPS (443) from anywhere
     - Allow PostgreSQL (5432) from your app IP (if DB on different instance)

3. Launch instance

### Step 2: Connect and Initial Setup

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@<your-ec2-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql-client nginx

# Install gunicorn globally (or use venv)
sudo pip3 install gunicorn
```

### Step 3: Deploy Application

```bash
# Clone your repository
cd /home/ubuntu
git clone <your-repo-url> diabetes-tracker
cd diabetes-tracker

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

Add to `.env`:
```
DB_HOST=localhost  # or your DB EC2 IP if separate
DB_PORT=5432
DB_NAME=diabetes_tracker
DB_USER=postgres
DB_PASSWORD=<your-password>
OPENAI_API_KEY=<your-key>
FLASK_ENV=production
```

### Step 4: Test Application

```bash
# Test run
gunicorn --bind 0.0.0.0:5000 --workers 2 'main:app'

# If it works, stop it (Ctrl+C) and continue
```

### Step 5: Create Systemd Service

```bash
sudo nano /etc/systemd/system/diabetes-tracker.service
```

Add:
```ini
[Unit]
Description=Diabetes Tracker Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/diabetes-tracker
Environment="PATH=/home/ubuntu/diabetes-tracker/venv/bin"
ExecStart=/home/ubuntu/diabetes-tracker/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /var/log/diabetes-tracker/access.log \
    --error-logfile /var/log/diabetes-tracker/error.log \
    'main:app'

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create log directory:
```bash
sudo mkdir -p /var/log/diabetes-tracker
sudo chown ubuntu:ubuntu /var/log/diabetes-tracker
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable diabetes-tracker
sudo systemctl start diabetes-tracker
sudo systemctl status diabetes-tracker
```

### Step 6: Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/diabetes-tracker
```

Add:
```nginx
server {
    listen 80;
    server_name <your-domain-or-ip>;

    # Serve static files directly
    location /static/ {
        alias /home/ubuntu/diabetes-tracker/src/diabetes_tracker/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy all other requests to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/diabetes-tracker /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### Step 7: Setup HTTPS with Let's Encrypt (Optional but Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

### Step 8: Configure Firewall

```bash
# Allow nginx
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### Step 9: Running App and DB on Same Instance

If you want to run both on the same EC2 instance:

1. **Install PostgreSQL** (if not already installed):
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. **Configure PostgreSQL** (see your existing setup guide)
3. **Update .env** to use `localhost` as DB_HOST
4. **Security Group:** Only need to allow HTTP/HTTPS, not PostgreSQL from outside

**Benefits:**
- Single instance = lower cost
- No network latency between app and DB
- Simpler security (no cross-instance networking)

**Considerations:**
- Both app and DB compete for resources
- If one crashes, both are down
- Harder to scale independently

### Step 10: Monitoring and Maintenance

```bash
# View app logs
sudo journalctl -u diabetes-tracker -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check app status
sudo systemctl status diabetes-tracker

# Restart app
sudo systemctl restart diabetes-tracker
```

### Deployment Updates

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<your-ec2-ip>

# Navigate to app directory
cd /home/ubuntu/diabetes-tracker

# Pull latest changes
git pull

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart diabetes-tracker
```

---

## Detailed Comparison: EC2 vs App Runner vs Lightsail

### Cost Breakdown

| Service | First Year | After First Year | Notes |
|---------|-----------|------------------|-------|
| **EC2 t3.micro** | **$0** (free tier) | ~$7.50/month | 750 hours/month free |
| **EC2 t2.micro** | **$0** (free tier) | ~$8/month | Burstable performance |
| **App Runner** | ~$2-5/month | ~$2-5/month | Pay per use, scales to zero |
| **Lightsail** | $3.50-5/month | $3.50-5/month | Fixed pricing |

### Feature Comparison

| Feature | EC2 | App Runner | Lightsail |
|---------|-----|------------|-----------|
| **Setup Complexity** | Medium | Medium (Docker) | Low |
| **Server Management** | You manage | AWS manages | You manage |
| **Scaling** | Manual | Automatic | Manual |
| **HTTPS** | Manual (Let's Encrypt) | Automatic | Manual (Let's Encrypt) |
| **Deployments** | Manual (SSH + git) | Automatic (from ECR/GitHub) | Manual (SSH + git) |
| **Monitoring** | CloudWatch (setup needed) | Built-in CloudWatch | Built-in dashboard |
| **Docker Required** | No | Yes | No |
| **Same Instance as DB** | ✅ Yes | ❌ No | ❌ No |
| **Free Tier** | ✅ Yes (12 months) | ❌ No | ❌ No |
| **Control Level** | Full | Limited | Full |
| **Best For** | Free tier, same instance as DB | Low traffic, minimal ops | Predictable cost, simple |

### Network Architecture

**EC2 (Same Instance):**
```
Internet → EC2 Instance
           ├── Flask App (port 5000)
           ├── Nginx (port 80/443)
           └── PostgreSQL (port 5432)
```

**EC2 (Separate Instances):**
```
Internet → EC2 App Instance → EC2 DB Instance
           ├── Flask App
           └── Nginx
```

**App Runner:**
```
Internet → App Runner → EC2 DB Instance
           (Auto HTTPS, Load Balancer)
```

**Lightsail:**
```
Internet → Lightsail Instance → EC2 DB Instance
           ├── Flask App
           └── Nginx
```

---

## Decision Matrix: Which Should You Choose?

### Choose **EC2** if:
- ✅ You're in AWS free tier (first 12 months) → **$0/month**
- ✅ You want to run app and database on the same instance (save costs)
- ✅ You want full control over the server
- ✅ You're comfortable managing servers and deployments
- ✅ You want to use the same VPC/security group as your database

### Choose **App Runner** if:
- ✅ You want the cheapest option after free tier (~$2-5/month)
- ✅ You want minimal server management
- ✅ You want automatic HTTPS and scaling
- ✅ You're okay with Docker/containerization
- ✅ Your database is on a separate EC2 instance

### Choose **Lightsail** if:
- ✅ You want predictable fixed pricing ($3.50-5/month)
- ✅ You want simple VPS-like setup (no Docker)
- ✅ You want more control than App Runner but less than EC2
- ✅ You prefer fixed costs over pay-per-use

### Quick Decision Tree

```
Are you in AWS free tier (first 12 months)?
├─ YES → Use EC2 t3.micro ($0/month) ✅
└─ NO → Continue...

Do you want to run app and DB on same instance?
├─ YES → Use EC2 (can use same instance) ✅
└─ NO → Continue...

Do you want minimal management?
├─ YES → Use App Runner ($2-5/month) ✅
└─ NO → Continue...

Do you want predictable fixed pricing?
├─ YES → Use Lightsail ($3.50-5/month) ✅
└─ NO → Use App Runner ($2-5/month) ✅
```

---

## Summary

**For your situation (database already on EC2, side project, low traffic):**

1. **If in free tier:** Use **EC2** - it's free for 12 months
2. **If past free tier:** Use **App Runner** - cheapest at ~$2-5/month
3. **If you want same instance as DB:** Use **EC2** - can run both together
4. **If you want simplest setup:** Use **Lightsail** - fixed $3.50-5/month, no Docker

**My recommendation:** Since your database is already on EC2, consider:
- **Option A:** Run app on the same EC2 instance (if it has enough resources) → **$0/month** (free tier) or **$7.50/month** after
- **Option B:** Use App Runner for the app, keep DB on EC2 → **~$2-5/month** for app + existing EC2 cost for DB

---

## Security Best Practices

1. **Environment Variables:**
   - Never commit `.env` files
   - Use AWS Secrets Manager or Parameter Store for sensitive data

2. **Database:**
   - Use VPC peering between App Runner and EC2 (if possible)
   - Or restrict EC2 security group to App Runner's IP range
   - Use strong passwords

3. **HTTPS:**
   - App Runner provides HTTPS automatically
   - Lightsail: Use Let's Encrypt for free SSL

4. **API Keys:**
   - Store OpenAI API key in AWS Secrets Manager
   - Reference in App Runner environment variables

---

## Monitoring and Logs

### App Runner
- View logs in CloudWatch
- Monitor metrics in App Runner dashboard

### Lightsail
- View logs: `journalctl -u diabetes-tracker -f`
- Monitor in Lightsail dashboard

---

## Troubleshooting

### Database Connection Issues
- Check EC2 security group allows connections from App Runner
- Verify DB credentials in environment variables
- Test connection: `psql -h <db-host> -U postgres -d diabetes_tracker`

### App Not Starting
- Check CloudWatch logs (App Runner) or system logs (Lightsail)
- Verify PORT environment variable matches Dockerfile
- Check gunicorn is installed

### Static Files Not Loading
- Verify static folder path in Flask app configuration
- Check file permissions

---

## Next Steps

1. Choose your deployment option (recommend App Runner)
2. Set up Docker (if using App Runner)
3. Configure environment variables
4. Deploy and test
5. Set up monitoring and alerts

