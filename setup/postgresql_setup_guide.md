# PostgreSQL Setup Guide for AWS EC2

## Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@18.188.44.175
```

## Step 2: Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

## Step 3: Start PostgreSQL Service

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

## Step 4: Configure PostgreSQL for Remote Connections

### 4.1 Set PostgreSQL Password

```bash
sudo -u postgres psql
```

In the PostgreSQL prompt:
```sql
ALTER USER postgres PASSWORD 'your-secure-password';
CREATE DATABASE diabetes_tracker;
\q
```

### 4.2 Configure PostgreSQL to Listen on All Interfaces

Edit the main configuration file:
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Find the line with `listen_addresses` and change it to:
```
listen_addresses = '*'
```

### 4.3 Configure Client Authentication

Edit the client authentication configuration:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add these lines at the end of the file:
```
# Allow remote connections
host    all             all             0.0.0.0/0               md5
host    all             all             ::/0                    md5
```

### 4.4 Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

## Step 5: Configure AWS Security Group

1. Go to AWS Console → EC2 → Security Groups
2. Find your EC2 instance's security group
3. Add inbound rule:
   - Type: PostgreSQL
   - Protocol: TCP
   - Port: 5432
   - Source: Your IP address (or 0.0.0.0/0 for testing)

## Step 6: Test Connection

### From EC2 instance:
```bash
psql -h localhost -U postgres -d diabetes_tracker
```

### From your local machine:
```bash
psql -h 18.188.44.175 -p 5432 -U postgres -d diabetes_tracker
```

## Step 7: Update Your .env File

Create a `.env` file in your project root:
```bash
cp env.example .env
```

Edit `.env` with your database credentials:
```
DB_HOST=18.188.44.175
DB_PORT=5432
DB_NAME=diabetes_tracker
DB_USER=postgres
DB_PASSWORD=your-secure-password
```

## Troubleshooting

### Check if PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

### Check if PostgreSQL is listening:
```bash
sudo netstat -tlnp | grep 5432
```

### Check PostgreSQL logs:
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Test connection from EC2:
```bash
telnet localhost 5432
```

### Check firewall:
```bash
sudo ufw status
```

If UFW is active, allow PostgreSQL:
```bash
sudo ufw allow 5432/tcp
```

## Security Considerations

For production use:
1. Use a dedicated database user instead of 'postgres'
2. Restrict security group to specific IP addresses
3. Use SSL connections
4. Consider using AWS RDS instead of self-managed PostgreSQL 