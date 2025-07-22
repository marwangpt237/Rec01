# Deployment Guide

## 🚀 Deployment Options

This OSINT Face Recognition Simulator can be deployed in several ways. Due to the complexity of OpenCV and computer vision dependencies, some deployment platforms may require special configuration.

## ⚠️ Known Issues

### OpenCV Compatibility
- **Issue**: OpenCV and NumPy have complex binary dependencies that may not work on all cloud platforms
- **Symptoms**: ImportError related to numpy._core._multiarray_umath
- **Solution**: Use platforms with full Python environment support or Docker deployment

## 🏠 Local Development (Recommended)

The most reliable way to run the application:

```bash
# Clone and setup
git clone <repository>
cd osint-face-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

Access at: `http://localhost:5000`

## 🐳 Docker Deployment (Recommended for Production)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p src/face_data/uploads src/face_data/known_faces

EXPOSE 5000

CMD ["python", "src/main.py"]
```

Build and run:
```bash
docker build -t osint-face-app .
docker run -p 5000:5000 osint-face-app
```

## ☁️ Cloud Platform Deployment

### 1. Heroku (with Buildpacks)

Add to your repository:

**`requirements.txt`** (simplified for Heroku):
```
Flask==3.1.1
flask-cors==6.0.0
Flask-SQLAlchemy==3.1.1
Pillow==10.0.1
requests==2.31.0
gunicorn==21.2.0
```

**`.buildpacks`**:
```
https://github.com/heroku/heroku-buildpack-apt
https://github.com/heroku/heroku-buildpack-python
```

**`Aptfile`**:
```
libsm6
libxext6
libxrender-dev
libglib2.0-0
libgtk-3-0
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### 2. Railway (Alternative Configuration)

Create `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python src/main.py"

[env]
PYTHONPATH = "/app"
```

### 3. DigitalOcean App Platform

Create `.do/app.yaml`:
```yaml
name: osint-face-app
services:
- name: web
  source_dir: /
  github:
    repo: your-username/osint-face-app
    branch: main
  run_command: python src/main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 5000
  routes:
  - path: /
```

## 🖥️ VPS/Server Deployment

### Using Gunicorn (Production)

1. **Install on server**:
```bash
pip install gunicorn
```

2. **Create gunicorn config** (`gunicorn.conf.py`):
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

3. **Run with Gunicorn**:
```bash
gunicorn -c gunicorn.conf.py src.main:app
```

### Using Nginx (Reverse Proxy)

**`/etc/nginx/sites-available/osint-face-app`**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase upload size for images
    client_max_body_size 10M;
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/osint-face-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Troubleshooting Deployment Issues

### OpenCV Import Errors

**Problem**: `ImportError: No module named 'cv2'`
**Solution**:
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install python3-opencv
# OR
pip install opencv-python-headless  # Lighter version
```

### NumPy Compatibility Issues

**Problem**: `ImportError: numpy._core._multiarray_umath`
**Solution**:
```bash
# Reinstall numpy and opencv
pip uninstall numpy opencv-python
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78
```

### Memory Issues

**Problem**: Application crashes due to memory limits
**Solution**:
- Use smaller image processing
- Implement image resizing before processing
- Increase server memory allocation

### Permission Issues

**Problem**: Cannot create directories or write files
**Solution**:
```bash
# Ensure proper permissions
chmod 755 src/face_data/
chmod 755 src/face_data/uploads/
chmod 755 src/face_data/known_faces/
```

## 🔒 Production Security Checklist

- [ ] Change Flask secret key
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Implement proper logging
- [ ] Set up monitoring
- [ ] Regular security updates
- [ ] Backup procedures

## 📊 Performance Optimization

### For High Traffic
- Use Redis for session storage
- Implement image caching
- Use CDN for static files
- Database connection pooling
- Load balancing with multiple instances

### For Resource Constraints
- Reduce image processing quality
- Implement request queuing
- Use lighter OpenCV build
- Optimize face detection parameters

## 🆘 Alternative Deployment Strategy

If OpenCV deployment continues to be problematic, consider:

1. **Simplified Version**: Remove OpenCV dependency and use basic image processing
2. **API-Only Deployment**: Deploy backend separately from frontend
3. **Containerized Deployment**: Use Docker with pre-built OpenCV images
4. **Local Network Deployment**: Run on local server with port forwarding

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review platform-specific documentation
3. Consider using Docker for consistent environments
4. Test locally before deploying to production

---

**Note**: Due to the complexity of computer vision dependencies, local development or Docker deployment is recommended for the most reliable experience.


## 🧠 Gemini API Deployment Considerations

### Environment Variables

For production deployments with Gemini integration, set the following environment variable:

```bash
# Required for Gemini AI features
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
```

### Platform-Specific Setup

#### Heroku
```bash
heroku config:set GOOGLE_AI_API_KEY=your-api-key-here
```

#### Railway
Add environment variable in Railway dashboard:
- Key: `GOOGLE_AI_API_KEY`
- Value: `your-api-key-here`

#### DigitalOcean App Platform
Add to `.do/app.yaml`:
```yaml
envs:
- key: GOOGLE_AI_API_KEY
  value: your-api-key-here
  type: SECRET
```

#### Docker
```dockerfile
ENV GOOGLE_AI_API_KEY=your-api-key-here
# Or use Docker secrets for better security
```

### API Key Security Best Practices

1. **Never commit API keys to version control**
2. **Use platform-specific secret management**
3. **Rotate keys regularly**
4. **Monitor API usage and costs**
5. **Set up usage quotas and alerts**

### Graceful Degradation

The application is designed to work with or without Gemini API access:

- **With API Key**: Full AI-enhanced analysis capabilities
- **Without API Key**: Traditional face recognition and basic OSINT only
- **API Failures**: Automatic fallback to traditional methods

### Performance Optimization

#### Caching Strategies
```python
# Example: Cache Gemini results to reduce API calls
import functools
import hashlib

@functools.lru_cache(maxsize=100)
def cached_gemini_analysis(image_hash):
    # Implementation details
    pass
```

#### Rate Limiting
```python
# Example: Implement rate limiting for API calls
from time import sleep
import threading

class GeminiRateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        # Implementation details
```

### Monitoring and Alerting

#### API Usage Monitoring
- Track API call frequency and costs
- Monitor response times and error rates
- Set up alerts for quota limits

#### Health Checks
```python
# Example health check endpoint
@app.route('/health/gemini')
def gemini_health():
    analyzer = get_gemini_analyzer()
    return {
        'status': 'healthy' if analyzer.is_enabled() else 'degraded',
        'gemini_available': analyzer.is_enabled()
    }
```

### Cost Management

#### API Cost Optimization
- Implement result caching where appropriate
- Use appropriate model sizes (gemini-1.5-flash vs gemini-1.5-pro)
- Monitor and set budget alerts in Google Cloud Console
- Implement usage quotas per user/session if needed

#### Resource Planning
- Estimate API costs based on expected usage
- Plan for traffic spikes and scaling
- Consider implementing usage tiers or limits

### Troubleshooting Gemini Integration

#### Common Issues

**API Key Not Working**
```bash
# Test API key manually
curl -H "Authorization: Bearer $GOOGLE_AI_API_KEY" \
     https://generativelanguage.googleapis.com/v1beta/models
```

**Import Errors**
```bash
# Verify google-generativeai installation
pip show google-generativeai
pip install --upgrade google-generativeai
```

**Rate Limiting**
- Check Google Cloud Console for quota limits
- Implement exponential backoff for retries
- Consider upgrading API quotas if needed

**Model Availability**
- Check Google AI Studio for model status
- Implement fallback to different models if needed
- Monitor Google's status page for service updates

### Testing in Production

#### Deployment Checklist
- [ ] API key configured and tested
- [ ] Gemini integration test script passes
- [ ] Fallback mechanisms working
- [ ] Monitoring and alerting configured
- [ ] Cost controls implemented
- [ ] Performance benchmarks established

#### Rollback Plan
- [ ] Ability to disable Gemini features via environment variable
- [ ] Traditional analysis methods fully functional
- [ ] Database rollback procedures (if applicable)
- [ ] User communication plan for feature changes

---

**Note**: The application is designed to be resilient and will continue to function even if Gemini API is unavailable, ensuring a reliable user experience regardless of external service status.

