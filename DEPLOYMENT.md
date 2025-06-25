# Writingway Web Deployment Guide

This guide covers different deployment options for Writingway Web.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Domain name (for production)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Writingway

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit environment files with your configuration
# backend/.env - Add your AI API keys
# frontend/.env - Set your API URL

# Start the application
docker-compose up -d
```

### Production Configuration

1. **Update environment variables:**
   ```bash
   # backend/.env
   DATABASE_URL=postgresql://user:password@db:5432/writingway
   SECRET_KEY=your-super-secret-key-here
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   
   # frontend/.env
   REACT_APP_API_URL=https://your-domain.com/api
   ```

2. **Use PostgreSQL for production:**
   ```yaml
   # Add to docker-compose.yml
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: writingway
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

3. **Configure reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://frontend:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🚀 Manual Deployment

### Backend Deployment

1. **Setup Python environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run with Gunicorn (production):**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Frontend Deployment

1. **Build the application:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Serve with Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       root /path/to/frontend/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## ☁️ Cloud Deployment

### Heroku

1. **Backend (Heroku):**
   ```bash
   # Create Heroku app
   heroku create writingway-api
   
   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set OPENAI_API_KEY=your-openai-key
   
   # Deploy
   git subtree push --prefix backend heroku main
   ```

2. **Frontend (Vercel/Netlify):**
   ```bash
   # Build command: npm run build
   # Publish directory: build
   # Environment variables: REACT_APP_API_URL
   ```

### AWS/GCP/Azure

- Use container services (ECS, Cloud Run, Container Instances)
- Set up managed databases (RDS, Cloud SQL, Azure Database)
- Configure load balancers and CDN

## 🔒 Security Considerations

1. **Environment Variables:**
   - Never commit `.env` files
   - Use strong secret keys
   - Rotate API keys regularly

2. **Database Security:**
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

3. **HTTPS:**
   - Use SSL certificates (Let's Encrypt)
   - Redirect HTTP to HTTPS
   - Set secure headers

## 📊 Monitoring

1. **Application Monitoring:**
   - Use application performance monitoring (APM)
   - Set up error tracking (Sentry)
   - Monitor API response times

2. **Infrastructure Monitoring:**
   - Monitor server resources
   - Set up alerts for downtime
   - Track database performance

## 🔄 Updates

1. **Backup before updates:**
   ```bash
   # Backup database
   docker-compose exec db pg_dump -U user writingway > backup.sql
   ```

2. **Update application:**
   ```bash
   git pull origin main
   docker-compose down
   docker-compose up --build -d
   ```

3. **Database migrations:**
   ```bash
   # If using Alembic
   docker-compose exec backend alembic upgrade head
   ```

## 🆘 Troubleshooting

### Common Issues

1. **CORS errors:**
   - Check `ALLOWED_ORIGINS` in backend config
   - Verify frontend API URL

2. **Database connection errors:**
   - Check database credentials
   - Ensure database is running
   - Verify network connectivity

3. **AI API errors:**
   - Verify API keys are correct
   - Check API quotas and limits
   - Monitor API usage

### Logs

```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Application logs
tail -f backend/logs/app.log
```

For more help, check the GitHub issues or join our Discord community.
