# App Runner Deployment Guide - Step by Step

## Prerequisites Checklist

- [ ] AWS Account with credits
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Docker installed locally
- [ ] Your EC2 database is running and accessible
- [ ] You know your database connection details (host, port, name, user, password)
- [ ] You have your OpenAI API key (if using AI features)

---

## Step 1: Prepare Your Database

Make sure your EC2 database allows connections from App Runner:

1. **Check your EC2 Security Group:**
   - Go to EC2 Console → Security Groups
   - Find the security group attached to your database instance
   - Add inbound rule:
     - Type: PostgreSQL
     - Port: 5432
     - Source: `0.0.0.0/0` (for testing) OR App Runner's VPC (more secure)
   - Save rules

2. **Verify database is accessible:**
   ```bash
   # Test from your local machine
   psql -h <your-ec2-ip> -p 5432 -U postgres -d diabetes_tracker
   ```

---

## Step 2: Create ECR Repository

1. **Go to AWS Console → ECR (Elastic Container Registry)**

2. **Create repository:**
   - Click "Create repository"
   - Visibility: Private
   - Repository name: `diabetes-tracker`
   - Tag immutability: Disabled (for now)
   - Scan on push: Optional
   - Click "Create repository"

3. **Note your repository URI:**
   - It will look like: `123456789012.dkr.ecr.us-east-1.amazonaws.com/diabetes-tracker`
   - Copy this - you'll need it

---

## Step 3: Build and Push Docker Image

### Option A: Using the deploy script (Easiest)

```bash
# Make sure you're in the project root
cd /Users/yc/Documents/HU/Final_Project/diabetes_tracker

# Get your AWS account ID
aws sts get-caller-identity --query Account --output text

# Run deploy script
./deploy.sh us-east-1 diabetes-tracker <your-aws-account-id>
```

### Option B: Manual steps

```bash
# 1. Get your AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-2"  # Change to your preferred region
REPO_NAME="diabetes-tracker"

# 2. Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# 3. Build the image
docker build -t $REPO_NAME:latest .

# 4. Tag the image
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

# 5. Push the image
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
```

**Expected output:** You should see the image being pushed successfully.

---

## Step 4: Create App Runner Service

1. **Go to AWS Console → App Runner**

2. **Click "Create service"**

3. **Source configuration:**
   - Source: **Container registry**
   - Provider: **Amazon ECR**
   - Container image URI: Click "Browse" and select your `diabetes-tracker` repository
   - Deployment trigger: **Manual** (or Automatic if you want auto-deploy on push)

4. **Configure service:**
   - **Service name:** `diabetes-tracker`
   - **Virtual CPU:** `0.25 vCPU` (cheapest option)
   - **Memory:** `0.5 GB` (cheapest option)
   - **Port:** `8000` (must match Dockerfile)
   - **Start command:** (leave empty - handled by Dockerfile)
   - **Environment variables:** Click "Add" and add these:

   ```
   DB_HOST=<your-ec2-ip-or-domain>
   DB_PORT=5432
   DB_NAME=diabetes_tracker
   DB_USER=postgres
   DB_PASSWORD=<your-db-password>
   OPENAI_API_KEY=<your-openai-api-key>
   FLASK_ENV=production
   PORT=8000
   ```

   **Important:** 
   - Replace `<your-ec2-ip-or-domain>` with your actual EC2 instance IP or domain
   - Replace `<your-db-password>` with your actual database password
   - Replace `<your-openai-api-key>` with your actual OpenAI API key

5. **Auto scaling:**
   - Min concurrency: `1`
   - Max concurrency: `10` (adjust based on expected traffic)
   - Max size: `1` (for low traffic)

6. **Health check:**
   - Health check path: `/health` (recommended - uses dedicated health endpoint)
   - Health check interval: `10` seconds
   - Health check timeout: `5` seconds
   - Healthy threshold: `1`
   - Unhealthy threshold: `5`
   
   **Note:** The app has a dedicated `/health` endpoint that returns JSON. Using `/` also works but `/health` is more explicit.

7. **Review and create:**
   - Review all settings
   - Click "Create & deploy"

---

## Step 5: Wait for Deployment

1. **App Runner will:**
   - Pull your Docker image
   - Create the service
   - Run health checks
   - This takes about 5-10 minutes

2. **Monitor the deployment:**
   - You'll see "Creating" → "Running" status
   - Check the "Logs" tab for any errors

3. **Get your service URL:**
   - Once running, you'll see a URL like: `https://xxxxx.us-east-1.awsapprunner.com`
   - Copy this URL

---

## Step 6: Test Your Deployment

1. **Test the homepage:**
   ```bash
   curl https://your-app-runner-url.us-east-1.awsapprunner.com/
   ```
   Should return HTML (your index.html)

2. **Test API endpoint:**
   ```bash
   curl https://your-app-runner-url.us-east-1.awsapprunner.com/api/user-stats/testuser
   ```
   (Replace `testuser` with a real username if you have one)

3. **Open in browser:**
   - Navigate to your App Runner URL
   - Test the full application

---

## Step 7: Update Database Security (Recommended)

Once your app is working, make it more secure:

1. **Get App Runner's VPC/Subnet:**
   - Go to App Runner service → Configuration → Networking
   - Note the VPC and subnet

2. **Update EC2 Security Group:**
   - Instead of `0.0.0.0/0`, restrict to App Runner's IP range
   - Or use VPC peering if both are in same region

---

## Troubleshooting

### Service won't start / Health check fails

1. **Check logs:**
   - Go to App Runner → Your service → Logs
   - Look for errors - the startup script provides detailed diagnostics
   - Check for messages like "Starting Diabetes Tracker Application"

2. **Common issues:**

   **Missing gunicorn (most common):**
   - **Symptom:** Logs show "gunicorn: command not found" or "Gunicorn not found"
   - **Fix:** Ensure `gunicorn==21.2.0` is in `requirements.txt` and rebuild image
   - **Verify:** Check logs for "Gunicorn version: ..." message

   **start.sh not running:**
   - **Symptom:** No diagnostic output in logs, container exits immediately
   - **Fix:** Ensure Dockerfile has `CMD ["sh", "-c", "./start.sh"]` and `start.sh` is executable
   - **Verify:** Check Dockerfile has `RUN chmod +x start.sh`

   **Database connection error:**
   - **Symptom:** Logs show "Failed to initialize DataManager" or connection timeouts
   - **Fix:** Check DB_HOST, DB_PASSWORD, and security group
   - **Verify:** Ensure EC2 security group allows inbound connections on port 5432

   **Port mismatch:**
   - **Symptom:** Health checks fail, service shows as unhealthy
   - **Fix:** Ensure PORT=8000 in both Dockerfile ENV and App Runner environment variables
   - **Verify:** Check logs show "Starting gunicorn on port 8000..."

   **App import fails:**
   - **Symptom:** Logs show "App import failed" or Python import errors
   - **Fix:** Check that all Python dependencies are in requirements.txt
   - **Verify:** Test locally with `python3 -c "from src.diabetes_tracker.app import app"`

3. **Debugging steps:**

   **Test Docker image locally:**
   ```bash
   # Build the image
   docker build -t diabetes-tracker-test .
   
   # Run with environment variables
   docker run -p 8000:8000 \
     -e DB_HOST=your-db-host \
     -e DB_PORT=5432 \
     -e DB_NAME=diabetes_tracker \
     -e DB_USER=postgres \
     -e DB_PASSWORD=your-password \
     -e OPENAI_API_KEY=your-key \
     diabetes-tracker-test
   
   # Check if it starts successfully
   # Look for the diagnostic output from start.sh
   ```

   **Test database connection:**
   ```bash
   # From App Runner logs, you should see connection attempts
   # Or test manually:
   psql -h <db-host> -U postgres -d diabetes_tracker
   ```

   **Check App Runner logs for specific errors:**
   - Look for lines starting with "ERROR:" or "✗"
   - Check if you see "Starting gunicorn on port..." (means start.sh ran)
   - Verify "App imported successfully" message appears

### Image build fails

- Check Dockerfile syntax
- Ensure all files are in the right place
- Check `.dockerignore` isn't excluding needed files (especially `start.sh` and `requirements.txt`)
- Verify gunicorn is in requirements.txt before building

### Container exits immediately

- Check App Runner logs for error messages
- Verify start.sh is executable: `RUN chmod +x start.sh` in Dockerfile
- Ensure CMD in Dockerfile uses: `CMD ["sh", "-c", "./start.sh"]`
- Check that gunicorn is installed (should see version in logs)

### Static files not loading

- Verify static folder path in Flask app
- Check file permissions in Docker image
- Ensure static files are copied in Dockerfile (should be included in `COPY . .`)

---

## Updating Your Deployment

### Option 1: Manual Update

```bash
# Rebuild and push new image
./deploy.sh us-east-1 diabetes-tracker <your-aws-account-id>

# In App Runner console, click "Deploy" → "Deploy latest revision"
```

### Option 2: Automatic Updates (Recommended)

1. **In App Runner service settings:**
   - Change "Deployment trigger" to **Automatic**
   - App Runner will auto-deploy when you push a new image

2. **To deploy:**
   ```bash
   # Just push new image
   ./deploy.sh us-east-1 diabetes-tracker <your-aws-account-id>
   # App Runner will automatically deploy
   ```

---

## Cost Monitoring

- **Check your costs:**
  - Go to AWS Cost Explorer
  - Filter by "App Runner"
  - Monitor your usage

- **Expected costs:**
  - Low traffic: ~$2-5/month
  - With credits: Should be covered

---

## Next Steps

- [ ] Set up custom domain (optional)
- [ ] Configure CloudWatch alarms for monitoring
- [ ] Set up CI/CD pipeline (GitHub Actions → ECR → App Runner)
- [ ] Review security settings
- [ ] Test all features end-to-end

---

## Quick Reference

**Your App Runner URL:**
```
https://xxxxx.us-east-1.awsapprunner.com
```

**ECR Repository:**
```
<account-id>.dkr.ecr.<region>.amazonaws.com/diabetes-tracker
```

**Deploy command:**
```bash
./deploy.sh us-east-1 diabetes-tracker <account-id>
```

