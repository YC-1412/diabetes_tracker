# EC2 Deployment Guide - Step by Step

## Is EC2 More Complicated?

**Short answer: Yes, but not by much.** Here's the comparison:

| Aspect | App Runner | EC2 |
|--------|------------|-----|
| **Setup Steps** | ~5 steps | ~8-10 steps |
| **Time to Deploy** | 10-15 minutes | 30-45 minutes |
| **Server Management** | None (AWS manages) | You manage (updates, security) |
| **HTTPS Setup** | Automatic | Manual (Let's Encrypt) |
| **Reverse Proxy** | Automatic | Manual (nginx) |
| **Deployments** | Push Docker image | SSH + git pull + restart |
| **Monitoring** | Built-in CloudWatch | Manual setup |
| **Cost** | ~$2-5/month | $0 (free tier) or ~$7.50/month |

**When to choose EC2:**
- ✅ You're in AWS free tier (first 12 months) → **$0/month**
- ✅ You want to run app and database on the same instance (save costs)
- ✅ You want full control over the server
- ✅ You're comfortable with SSH and Linux commands

**When to choose App Runner:**
- ✅ You want minimal setup and management
- ✅ You want automatic HTTPS and scaling
- ✅ You're okay with Docker/containerization

---

## Prerequisites Checklist

- [ ] AWS Account (free tier eligible for first 12 months)
- [ ] EC2 instance created (or will create one)
- [ ] SSH key pair for EC2 access
- [ ] Your database is running (on same EC2 or separate instance)
- [ ] You know your database connection details
- [ ] You have your OpenAI API key (if using AI features)
- [ ] Basic familiarity with Linux commands and SSH

---

## Step 1: Create EC2 Instance

1. **Go to AWS Console → EC2 → Launch Instance**

2. **Configure instance:**
   - **Name:** `diabetes-tracker-app` (optional)
   - **AMI:** Ubuntu 22.04 LTS (free tier eligible)
   - **Instance type:** 
     - `t2.micro` or `t3.micro` (free tier eligible)
     - If running app + DB on same instance: `t3.small` (not free tier, ~$15/month)
   - **Key pair:** Create new or select existing
     - ⚠️ **Important:** Download and save the `.pem` file securely
   - **Network settings:**
     - Allow SSH (22) from your IP
     - Allow HTTP (80) from anywhere (0.0.0.0/0)
     - Allow HTTPS (443) from anywhere (0.0.0.0/0)
   - **Storage:** 8 GB (free tier) or 20 GB (recommended)

3. **Launch instance**

4. **Note your instance details:**
   - Public IP address
   - Instance ID
   - Security group name

---

## Step 2: Connect to EC2 Instance

### Option A: SSH from Terminal (macOS/Linux)

```bash
# Set correct permissions on key file
chmod 400 your-key.pem

# Connect to instance
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

### Option B: AWS Systems Manager Session Manager (No SSH key needed)

1. Install Session Manager plugin (if not already installed)
2. In EC2 Console, select your instance → Connect → Session Manager
3. Click "Connect"

---

## Step 3: Initial Server Setup

Once connected to your EC2 instance:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-client \
    nginx \
    git \
    build-essential

# Install gunicorn globally (or we'll use venv)
sudo pip3 install gunicorn

# Verify installations
python3 --version
nginx -v
```

---

## Step 4: Deploy Application Code

### Option A: Clone from Git Repository (Recommended)

```bash
# Navigate to home directory
cd /home/ubuntu

# Clone your repository
git clone <your-repo-url> diabetes-tracker
cd diabetes-tracker

# If repository is private, you may need to:
# 1. Use SSH keys, or
# 2. Use GitHub personal access token
```

### Option B: Upload Files via SCP

```bash
# From your local machine
scp -i your-key.pem -r /path/to/diabetes_tracker ubuntu@<ec2-ip>:/home/ubuntu/
```

### Option C: Use AWS CodeDeploy (Advanced)

For automated deployments, set up CodeDeploy (more complex, not covered here).

---

## Step 5: Set Up Python Environment

```bash
# Navigate to project directory
cd /home/ubuntu/diabetes-tracker

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify gunicorn is installed
pip list | grep gunicorn
```

---

## Step 6: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add the following (replace with your actual values):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=diabetes_tracker
DB_USER=postgres
DB_PASSWORD=<your-db-password>
OPENAI_API_KEY=<your-openai-api-key>
FLASK_ENV=production
PORT=5000
```

**Important notes:**
- If database is on **same instance**: Use `DB_HOST=localhost`
- If database is on **different EC2 instance**: Use `DB_HOST=<other-ec2-ip>`
- Save and exit: `Ctrl+X`, then `Y`, then `Enter`

**Security tip:** For production, consider using AWS Secrets Manager or SSM Parameter Store instead of `.env` file.

---

## Step 7: Test the Application

```bash
# Make sure you're in the project directory with venv activated
cd /home/ubuntu/diabetes-tracker
source venv/bin/activate

# Test run the application
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 'main:app'
```

**Expected output:** You should see gunicorn starting up.

**Test from your browser:**
- Open `http://<your-ec2-ip>:5000` in your browser
- You should see your application

**If it works:**
- Stop the server: `Ctrl+C`
- Continue to next step

**If it doesn't work:**
- Check the error messages
- Verify database connection
- Verify all environment variables are set correctly

---

## Step 8: Create Systemd Service

Create a system service so the app runs automatically and restarts on failure:

```bash
# Create service file
sudo nano /etc/systemd/system/diabetes-tracker.service
```

Add the following content:

```ini
[Unit]
Description=Diabetes Tracker Flask App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
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

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

**Create log directory:**
```bash
sudo mkdir -p /var/log/diabetes-tracker
sudo chown ubuntu:ubuntu /var/log/diabetes-tracker
```

**Enable and start the service:**
```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable diabetes-tracker

# Start the service
sudo systemctl start diabetes-tracker

# Check status
sudo systemctl status diabetes-tracker
```

**Expected output:** You should see `active (running)` in green.

**View logs:**
```bash
# View service logs
sudo journalctl -u diabetes-tracker -f

# View application logs
tail -f /var/log/diabetes-tracker/error.log
```

---

## Step 9: Configure Nginx Reverse Proxy

Nginx will handle HTTP/HTTPS and proxy requests to your Flask app.

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/diabetes-tracker
```

Add the following (replace `<your-domain-or-ip>` with your EC2 IP or domain):

```nginx
server {
    listen 80;
    server_name <your-ec2-ip> <your-domain-if-any>;

    # Increase client body size limit (for file uploads if needed)
    client_max_body_size 10M;

    # Serve static files directly (more efficient)
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
        proxy_connect_timeout 120s;
    }
}
```

**Enable the site:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/diabetes-tracker /etc/nginx/sites-enabled/

# Remove default nginx site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
```

**Expected output:** `syntax is ok` and `test is successful`

**Start and enable nginx:**
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

**Test your application:**
- Open `http://<your-ec2-ip>` in your browser
- You should see your application (without port 5000)

---

## Step 10: Set Up HTTPS with Let's Encrypt (Optional but Recommended)

**Prerequisites:**
- You have a domain name pointing to your EC2 IP (or you can use the IP directly)
- Port 80 and 443 are open in your security group

**Install Certbot:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

**Get SSL certificate:**

**Option A: With domain name (Recommended)**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Option B: Without domain (IP only)**
- Let's Encrypt requires a domain name
- For IP-only, you can use self-signed certificate (not recommended for production):
  ```bash
  sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt
  ```
- Then update nginx config to use SSL (more complex, not covered here)

**Auto-renewal:**
Certbot automatically sets up renewal. Test it:
```bash
sudo certbot renew --dry-run
```

---

## Step 11: Configure Firewall

```bash
# Allow nginx
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Check status
sudo ufw status
```

---

## Step 12: Running App and Database on Same Instance (Optional)

If you want to run both the Flask app and PostgreSQL on the same EC2 instance:

### Install PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Configure PostgreSQL

Follow your existing PostgreSQL setup guide, or:

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE diabetes_tracker;
CREATE USER postgres WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE diabetes_tracker TO postgres;
\q
```

### Update .env file

```bash
nano /home/ubuntu/diabetes-tracker/.env
```

Change `DB_HOST=localhost` (if not already)

### Update Security Group

- Remove PostgreSQL (5432) inbound rule (not needed if DB is only accessed locally)
- Keep only HTTP (80), HTTPS (443), and SSH (22)

**Benefits:**
- Single instance = lower cost
- No network latency between app and DB
- Simpler security

**Considerations:**
- Both app and DB compete for resources
- If instance crashes, both are down
- Harder to scale independently

---

## Step 13: Test Your Deployment

1. **Test homepage:**
   ```bash
   curl http://<your-ec2-ip>/
   ```
   Should return HTML

2. **Test API endpoint:**
   ```bash
   curl http://<your-ec2-ip>/api/user-stats/testuser
   ```

3. **Open in browser:**
   - Navigate to `http://<your-ec2-ip>` or `https://<your-domain>`
   - Test the full application

---

## Updating Your Deployment

When you need to deploy updates:

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<your-ec2-ip>

# Navigate to app directory
cd /home/ubuntu/diabetes-tracker

# Pull latest changes (if using git)
git pull

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Restart the service
sudo systemctl restart diabetes-tracker

# Check status
sudo systemctl status diabetes-tracker

# View logs if needed
sudo journalctl -u diabetes-tracker -f
```

---

## Monitoring and Maintenance

### View Application Logs

```bash
# Service logs
sudo journalctl -u diabetes-tracker -f

# Application logs
tail -f /var/log/diabetes-tracker/error.log
tail -f /var/log/diabetes-tracker/access.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Check Service Status

```bash
# Check app service
sudo systemctl status diabetes-tracker

# Check nginx
sudo systemctl status nginx

# Check database (if on same instance)
sudo systemctl status postgresql
```

### Restart Services

```bash
# Restart app
sudo systemctl restart diabetes-tracker

# Restart nginx
sudo systemctl restart nginx

# Restart database (if on same instance)
sudo systemctl restart postgresql
```

### System Updates

```bash
# Update system packages (do this regularly)
sudo apt update && sudo apt upgrade -y

# Reboot if kernel updates were installed
sudo reboot
```

---

## Troubleshooting

### Service won't start

1. **Check service status:**
   ```bash
   sudo systemctl status diabetes-tracker
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u diabetes-tracker -n 50
   ```

3. **Common issues:**
   - **Port already in use:** Another process is using port 5000
   - **Database connection error:** Check DB credentials in `.env`
   - **Missing dependencies:** Run `pip install -r requirements.txt`
   - **Permission errors:** Check file ownership with `ls -la`

### Application not accessible

1. **Check nginx status:**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   ```

2. **Check security group:**
   - Ensure HTTP (80) and HTTPS (443) are allowed
   - Check EC2 Console → Security Groups

3. **Check firewall:**
   ```bash
   sudo ufw status
   ```

4. **Test app directly:**
   ```bash
   curl http://127.0.0.1:5000
   ```

### Database connection errors

1. **Test database connection:**
   ```bash
   psql -h localhost -U postgres -d diabetes_tracker
   # Or if DB is on different instance:
   psql -h <db-ip> -U postgres -d diabetes_tracker
   ```

2. **Check .env file:**
   ```bash
   cat /home/ubuntu/diabetes-tracker/.env
   ```

3. **Check security group:**
   - If DB is on different instance, ensure PostgreSQL (5432) is allowed from app instance

### Static files not loading

1. **Check nginx configuration:**
   ```bash
   sudo nginx -t
   ```

2. **Verify static folder path:**
   ```bash
   ls -la /home/ubuntu/diabetes-tracker/src/diabetes_tracker/static/
   ```

3. **Check file permissions:**
   ```bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/diabetes-tracker
   ```

---

## Cost Comparison

| Option | First Year | After First Year | Notes |
|--------|-----------|------------------|-------|
| **EC2 t3.micro** | **$0** (free tier) | ~$7.50/month | 750 hours/month free |
| **EC2 t2.micro** | **$0** (free tier) | ~$8/month | Burstable performance |
| **EC2 t3.small** (app + DB) | ~$15/month | ~$15/month | Not free tier |
| **App Runner** | ~$2-5/month | ~$2-5/month | Pay per use |

**Note:** EC2 free tier includes 750 hours/month of t2.micro or t3.micro for the first 12 months.

---

## Security Best Practices

1. **Environment Variables:**
   - Use AWS Secrets Manager or SSM Parameter Store instead of `.env` file
   - Never commit `.env` files to git

2. **SSH Access:**
   - Use SSH keys, not passwords
   - Restrict SSH access to your IP only
   - Consider using AWS Systems Manager Session Manager

3. **Firewall:**
   - Only open necessary ports
   - Use security groups to restrict access

4. **Updates:**
   - Regularly update system packages: `sudo apt update && sudo apt upgrade -y`
   - Keep Python dependencies updated

5. **HTTPS:**
   - Always use HTTPS in production
   - Set up Let's Encrypt for free SSL certificates

6. **Database:**
   - Use strong passwords
   - Restrict database access to app instance only
   - Consider using AWS RDS for managed database

---

## Quick Reference

**SSH into instance:**
```bash
ssh -i your-key.pem ubuntu@<ec2-ip>
```

**View app logs:**
```bash
sudo journalctl -u diabetes-tracker -f
```

**Restart app:**
```bash
sudo systemctl restart diabetes-tracker
```

**Deploy updates:**
```bash
cd /home/ubuntu/diabetes-tracker
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart diabetes-tracker
```

**Check service status:**
```bash
sudo systemctl status diabetes-tracker
sudo systemctl status nginx
```

---

## Next Steps

- [ ] Set up CloudWatch monitoring (optional)
- [ ] Configure automated backups
- [ ] Set up domain name and DNS
- [ ] Configure email alerts for errors
- [ ] Set up CI/CD pipeline (GitHub Actions → EC2)
- [ ] Review and harden security settings

---

## Summary: EC2 vs App Runner

**Choose EC2 if:**
- ✅ You're in AWS free tier → **$0/month**
- ✅ You want to run app and DB on same instance
- ✅ You want full control
- ✅ You're comfortable with server management

**Choose App Runner if:**
- ✅ You want minimal setup (~10 minutes vs ~45 minutes)
- ✅ You want automatic HTTPS and scaling
- ✅ You're okay with Docker
- ✅ You want less maintenance

**My recommendation:** If you're in the free tier, use EC2. If not, App Runner is simpler and cheaper for low traffic.

