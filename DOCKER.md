# Docker Deployment Guide

This guide covers how to deploy Family Voices using Docker with best practices for production environments.

## Quick Start

### Production Deployment

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at `http://localhost:8080`

### Development Environment

```bash
# Start development environment with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

The development server will be available at `http://localhost:5001`

## Docker Build Features

### Multi-stage Build
- **Builder stage**: Installs build dependencies and Python packages
- **Production stage**: Minimal runtime image with only necessary components

### Security Best Practices
- Non-root user execution
- Minimal attack surface with slim base image
- No unnecessary packages in production image
- Proper file permissions

### Performance Optimizations
- Layer caching optimization
- Minimal image size
- Health checks for container orchestration
- Gunicorn WSGI server for production

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Random | Flask secret key for sessions |
| `DATA_DIR` | `/app/data` | Directory for persistent data |
| `MAX_AUDIO_SIZE` | `20971520` | Maximum audio file size (20MB) |
| `MAX_IMAGE_SIZE` | `10485760` | Maximum image file size (10MB) |
| `FLASK_ENV` | `production` | Flask environment |

## Persistent Storage

User data is stored in Docker volumes:
- Audio recordings: `/app/data/audio/`
- Images: `/app/data/images/`
- Application data: `/app/data/data.json`

### Backup Data

```bash
# Create backup
docker run --rm -v family_voices_data:/data -v $(pwd):/backup alpine tar czf /backup/family-voices-backup.tar.gz -C /data .

# Restore backup
docker run --rm -v family_voices_data:/data -v $(pwd):/backup alpine tar xzf /backup/family-voices-backup.tar.gz -C /data
```

## Health Checks

The container includes built-in health checks:
- Endpoint: `GET /api/health`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## Production Deployment

### Using Docker Compose

1. **Set environment variables**:
   ```bash
   export SECRET_KEY="your-super-secret-production-key"
   ```

2. **Deploy**:
   ```bash
   docker-compose up -d
   ```

3. **Monitor**:
   ```bash
   docker-compose logs -f
   docker-compose ps
   ```

### Using Docker Swarm

```bash
# Initialize swarm (if not already done)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml family-voices

# Monitor services
docker service ls
docker service logs family-voices_family-voices
```

### Using Kubernetes

A Kubernetes deployment example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: family-voices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: family-voices
  template:
    metadata:
      labels:
        app: family-voices
    spec:
      containers:
      - name: family-voices
        image: family-voices:latest
        ports:
        - containerPort: 8080
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: family-voices-secret
              key: secret-key
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: family-voices-pvc
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps

# Rebuild image
docker-compose build --no-cache
```

### Health Check Failures
```bash
# Check health status
docker inspect $(docker-compose ps -q family-voices) | grep Health -A 10

# Test health endpoint manually
docker-compose exec family-voices curl http://localhost:8080/api/health
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check application logs
docker-compose logs family-voices

# Scale horizontally (if using swarm/k8s)
docker service scale family-voices_family-voices=3
```

## Security Considerations

1. **Change default secret key** in production
2. **Use HTTPS** with a reverse proxy (nginx/traefik)
3. **Regular updates** of base images
4. **Monitor logs** for suspicious activity
5. **Backup data** regularly
6. **Network isolation** using Docker networks
7. **Resource limits** to prevent DoS

### Example with Traefik (HTTPS)

```yaml
version: '3.8'

services:
  family-voices:
    # ... existing config ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.family-voices.rule=Host(\`voices.yourdomain.com\`)"
      - "traefik.http.routers.family-voices.tls.certresolver=letsencrypt"
      - "traefik.http.services.family-voices.loadbalancer.server.port=8080"
```
