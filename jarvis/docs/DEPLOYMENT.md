# Deployment Guide

This guide covers different deployment scenarios for Jarvis Voice Assistant, from development setups to production environments.

## 🏠 Local Development Deployment

### Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/Prophet60191/jarvis.git
cd jarvis
python -m venv jarvis-env
source jarvis-env/bin/activate  # On Windows: jarvis-env\Scripts\activate
pip install -r requirements.txt

# Install and configure Ollama
ollama serve &
ollama pull llama3.1:8b

# Start Jarvis
python start_jarvis.py
```

### Development Configuration

Create a `.env` file for development:
```bash
# Development settings
JARVIS_DEBUG=true
JARVIS_LOG_LEVEL=DEBUG
JARVIS_MODEL=llama3.1:8b
JARVIS_ENABLE_USER_PROFILE=true

# Optional: API keys for cloud services
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

## 🖥️ Desktop Deployment

### Single User Desktop Installation

**macOS/Linux**:
```bash
# Create application directory
sudo mkdir -p /opt/jarvis
sudo chown $USER:$USER /opt/jarvis
cd /opt/jarvis

# Clone and setup
git clone https://github.com/Prophet60191/jarvis.git .
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install desktop dependencies
python install_desktop.py

# Create startup script
cat > start_jarvis.sh << 'EOF'
#!/bin/bash
cd /opt/jarvis
source venv/bin/activate
python start_jarvis.py
EOF
chmod +x start_jarvis.sh

# Create desktop entry (Linux)
cat > ~/.local/share/applications/jarvis.desktop << 'EOF'
[Desktop Entry]
Name=Jarvis Voice Assistant
Comment=AI-powered voice assistant
Exec=/opt/jarvis/start_jarvis.sh
Icon=/opt/jarvis/assets/jarvis-icon.png
Terminal=false
Type=Application
Categories=Utility;
EOF
```

**Windows**:
```batch
REM Create batch file for startup
echo @echo off > start_jarvis.bat
echo cd /d "C:\Program Files\Jarvis" >> start_jarvis.bat
echo call venv\Scripts\activate >> start_jarvis.bat
echo python start_jarvis.py >> start_jarvis.bat

REM Create Windows service (optional)
python install_windows_service.py
```

### System Service Deployment

**systemd Service (Linux)**:
```bash
# Create service file
sudo cat > /etc/systemd/system/jarvis.service << 'EOF'
[Unit]
Description=Jarvis Voice Assistant
After=network.target

[Service]
Type=simple
User=jarvis
WorkingDirectory=/opt/jarvis
Environment=PATH=/opt/jarvis/venv/bin
ExecStart=/opt/jarvis/venv/bin/python start_jarvis.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

**launchd Service (macOS)**:
```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.jarvis.assistant.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/jarvis/venv/bin/python</string>
        <string>/opt/jarvis/start_jarvis.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/jarvis</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load service
launchctl load ~/Library/LaunchAgents/com.jarvis.assistant.plist
```

## 🌐 Network Deployment

### Multi-User Network Setup

For shared environments where multiple users access Jarvis:

```bash
# Server setup
# Install on central server
sudo mkdir -p /opt/jarvis-server
cd /opt/jarvis-server
git clone https://github.com/Prophet60191/jarvis.git .
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure for network access
cat > .env << 'EOF'
JARVIS_HOST=0.0.0.0
JARVIS_PORT=8080
JARVIS_ALLOW_REMOTE_ACCESS=true
JARVIS_MULTI_USER=true
EOF

# Start with network binding
python start_jarvis.py --host 0.0.0.0 --port 8080
```

**Client Access**:
```bash
# Clients can access via web interface
# http://server-ip:8080

# Or install lightweight client
pip install jarvis-client
jarvis-client connect --server http://server-ip:8080
```

## 🐳 Container Deployment

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8080 11434

# Start script
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

**docker-entrypoint.sh**:
```bash
#!/bin/bash
set -e

# Start Ollama in background
ollama serve &

# Wait for Ollama to be ready
sleep 5

# Pull model if not exists
if ! ollama list | grep -q "llama3.1:8b"; then
    ollama pull llama3.1:8b
fi

# Start Jarvis
exec python start_jarvis.py
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  jarvis:
    build: .
    ports:
      - "8080:8080"
      - "11434:11434"
    volumes:
      - jarvis_data:/app/data
      - jarvis_config:/root/.jarvis
    environment:
      - JARVIS_HOST=0.0.0.0
      - JARVIS_PORT=8080
    restart: unless-stopped

volumes:
  jarvis_data:
  jarvis_config:
```

**Deploy with Docker**:
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f jarvis

# Access web interface
# http://localhost:8080
```

## ☁️ Cloud Deployment

### VPS/Cloud Server Deployment

**Preparation**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    portaudio19-dev espeak espeak-data libespeak1 libespeak-dev \
    nginx certbot python3-certbot-nginx

# Create jarvis user
sudo useradd -m -s /bin/bash jarvis
sudo su - jarvis
```

**Installation**:
```bash
# Clone and setup as jarvis user
git clone https://github.com/Prophet60191/jarvis.git
cd jarvis
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.1:8b
```

**Nginx Configuration**:
```nginx
# /etc/nginx/sites-available/jarvis
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**SSL Setup**:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jarvis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## 🔒 Security Considerations

### Network Security

```bash
# Firewall configuration
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8080  # Block direct access to Jarvis port
sudo ufw enable
```

### Authentication Setup

For production deployments, add authentication:

```python
# In your deployment configuration
JARVIS_REQUIRE_AUTH=true
JARVIS_AUTH_SECRET=your-secret-key
JARVIS_ALLOWED_USERS=user1,user2,user3
```

### Data Protection

```bash
# Encrypt data directory
sudo apt install ecryptfs-utils
sudo ecryptfs-add-passphrase
sudo mount -t ecryptfs /opt/jarvis/data /opt/jarvis/data
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
# Check if Jarvis is responding
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "Jarvis is healthy"
    exit 0
else
    echo "Jarvis is not responding"
    exit 1
fi
EOF
chmod +x health_check.sh

# Add to crontab for monitoring
echo "*/5 * * * * /opt/jarvis/health_check.sh" | crontab -
```

### Log Management

```bash
# Setup log rotation
sudo cat > /etc/logrotate.d/jarvis << 'EOF'
/opt/jarvis/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/jarvis_$DATE"

mkdir -p $BACKUP_DIR
cp -r /opt/jarvis/data $BACKUP_DIR/
cp -r /root/.jarvis $BACKUP_DIR/
cp /opt/jarvis/.env $BACKUP_DIR/

tar -czf "/backup/jarvis_backup_$DATE.tar.gz" -C /backup "jarvis_$DATE"
rm -rf $BACKUP_DIR

# Keep only last 7 backups
find /backup -name "jarvis_backup_*.tar.gz" -mtime +7 -delete
EOF
chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /opt/jarvis/backup.sh" | crontab -
```

## 🚀 Performance Optimization

### Resource Optimization

```bash
# Optimize for production
export JARVIS_WORKERS=4
export JARVIS_MAX_MEMORY=8G
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=2
```

### Caching Configuration

```python
# Enable caching for better performance
JARVIS_ENABLE_CACHE=true
JARVIS_CACHE_TTL=3600
JARVIS_CACHE_SIZE=1000
```

This deployment guide covers various scenarios from development to production. Choose the deployment method that best fits your needs and environment.
