# Binance Portfolio Tracker

A full-stack application to track your Binance cryptocurrency portfolio with real-time data visualization. Built with Django, React, Docker, Nginx, Gunicorn, and PostgreSQL.

## Tech Stack

### Backend
- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - API development
- **Gunicorn 21.2.0** - Production WSGI server
- **PostgreSQL 15** - Database
- **Python 3.11** - Programming language
- **python-binance 1.0.19** - Binance API integration

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **Modern CSS** - Responsive design with gradients and animations

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx 1.25** - Reverse proxy and static file server
- **Git** - Version control

## Architecture

The application uses a production-ready microservices architecture:

```
Browser → React (port 3000) → Nginx (port 80) → Django API (port 8000) → Binance API
                                      ↓
                                 PostgreSQL
```

**Services:**
- `db`: PostgreSQL 15 database
- `web`: Django application with Gunicorn (3 workers) + Binance integration
- `nginx`: Nginx reverse proxy serving static files and proxying to Django
- `frontend`: React development server for portfolio UI

## Quick Start

### Prerequisites
- Docker
- Docker Compose
- Git

### Installation & Running

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd landing_page
   ```

2. **Environment Configuration**
   
   Create a `.env` file with your configuration:
   ```env
   DEBUG=True
   SECRET_KEY=django-insecure-change-this-in-production
   
   # Database
   DB_NAME=landing_page_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   
   # Binance API (Required)
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_api_secret_here
   BINANCE_TESTNET=False
   
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```
   
   > [!IMPORTANT]
   > **Binance API Keys**: You need to create API keys from your Binance account. Use **READ-ONLY** permissions for security.
   > 
   > How to get Binance API keys:
   > 1. Log in to [Binance](https://www.binance.com)
   > 2. Go to Account → API Management
   > 3. Create a new API key with **READ-ONLY** permissions
   > 4. Copy the API Key and Secret to your `.env` file

3. **Build and start containers**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - **Portfolio Dashboard**: **http://localhost:3000** (React frontend)
   - **Django API**: **http://localhost/api/portfolio/**
   - **Admin panel**: **http://localhost/admin** (after creating superuser)

### First Time Setup

Create a Django superuser for admin access:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Docker Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f frontend
docker-compose logs -f db

# Check service status
docker-compose ps

# Rebuild containers
docker-compose up -d --build
```

### Django Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Django shell
docker-compose exec web python manage.py shell
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d landing_page_db

# Backup database
docker-compose exec db pg_dump -U postgres landing_page_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres landing_page_db < backup.sql
```

## Project Structure

```
landing_page/
├── landing_page/          # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py       # Project settings (PostgreSQL + Binance)
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
├── portfolio/            # Portfolio Django app
│   ├── services/
│   │   └── binance_service.py  # Binance API integration
│   ├── views.py          # API views
│   └── urls.py           # Portfolio routes
├── frontend/             # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Portfolio.jsx   # Portfolio component
│   │   │   └── Portfolio.css   # Styling
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   ├── App.jsx
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── nginx/                # Nginx configuration
│   ├── Dockerfile        # Nginx Docker image
│   └── nginx.conf        # Nginx server configuration
├── venv/                 # Virtual environment (local dev only)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Django/Gunicorn Docker image
├── docker-compose.yml    # Docker services orchestration
├── entrypoint.sh         # Container startup script
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Configuration Details

### Database
- **Engine**: PostgreSQL (SQLite removed)
- **Host**: `db` (Docker service name)
- **Port**: 5432 (internal only)
- **Database**: `landing_page_db`

### Web Server
- **WSGI Server**: Gunicorn with 3 workers
- **Internal Port**: 8000 (not exposed externally)
- **Timeout**: 60 seconds

### Nginx
- **External Port**: 80
- **Static Files**: Served directly from `/app/staticfiles/`
- **Cache**: 30-day cache for static files
- **Proxy**: All dynamic requests proxied to Gunicorn

### React Frontend
- **Port**: 3000 (development server)
- **Auto-refresh**: Portfolio updates every 30 seconds
- **API URL**: `http://localhost/api`

### Binance Integration
- **API Endpoint**: `/api/portfolio/`
- **Test Endpoint**: `/api/portfolio/test/`
- **Features**:
  - Real-time portfolio balance
  - USD value calculation
  - Asset percentage distribution
  - Support for multiple trading pairs (USDT, BUSD, BTC)

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Django secret key (change in production!)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `DB_HOST`: Database host (`db` for Docker)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Development Workflow

### Making Code Changes

The `web` service mounts the current directory, so code changes are reflected immediately:

1. Edit your Django code
2. Gunicorn will auto-reload (in development mode)
3. Refresh your browser

For template or static file changes:
```bash
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart nginx
```

### Adding Python Dependencies

1. Add package to `requirements.txt`
2. Rebuild the web container:
   ```bash
   docker-compose up -d --build web
   ```

## Production Considerations

Before deploying to production:

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use strong database passwords
- [ ] **Use READ-ONLY Binance API keys**
- [ ] **Enable IP whitelist on Binance API keys**
- [ ] Configure SSL/TLS certificates for HTTPS
- [ ] Set up proper logging and monitoring
- [ ] Configure database backups
- [ ] Review Nginx security headers
- [ ] Set up environment-specific `.env` files

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Remove all containers and volumes, start fresh
docker-compose down -v
docker-compose up -d --build
```

### Database connection errors
```bash
# Ensure database is healthy
docker-compose ps

# Check database logs
docker-compose logs db
```

### Static files not loading
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput

# Restart nginx
docker-compose restart nginx
```

## Setup History

✅ **Environment Configuration**
- Created `.env` file with PostgreSQL and Binance API configuration
- Removed SQLite, using PostgreSQL exclusively

✅ **Docker Infrastructure**
- PostgreSQL 15 database with health checks
- Django application with Gunicorn WSGI server
- Nginx reverse proxy for production-like setup
- React development server for frontend

✅ **Django Project**
- Initialized Django project "landing_page"
- Configured for PostgreSQL only
- Applied all initial migrations
- Static files collection configured
- Created `portfolio` app for Binance integration

✅ **Binance API Integration**
- Integrated python-binance library
- Created Binance service for portfolio data
- REST API endpoints at `/api/portfolio/`
- CORS configured for React frontend
- Real-time portfolio balance and USD value calculation

✅ **React Frontend**
- Modern portfolio dashboard with gradient UI
- Auto-refresh every 30 seconds
- Responsive design with animations
- Asset cards with percentage bars
- Loading and error states

✅ **Production Ready**
- Nginx serving static files efficiently
- Gunicorn with multiple workers
- Shared volumes for static files
- Proper service dependencies and health checks
- Secure API key management

## Features

- 💼 **Real-time Portfolio Tracking**: View your Binance portfolio composition
- 💰 **USD Value Calculation**: Automatic conversion to USD for all assets
- 📊 **Visual Representation**: Asset percentage bars and cards
- 🔄 **Auto-refresh**: Portfolio updates every 30 seconds
- 🎨 **Modern UI**: Gradient design with smooth animations
- 🔒 **Secure**: API keys stored server-side only
- 🐳 **Docker Ready**: Complete containerized setup

## License

This project is currently in development phase.
