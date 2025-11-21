# Landing Page Project

A production-ready Django landing page application with Docker, Nginx, Gunicorn, and PostgreSQL.

## Tech Stack

### Backend
- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - API development
- **Gunicorn 21.2.0** - Production WSGI server
- **PostgreSQL 15** - Database
- **Python 3.11** - Programming language

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx 1.25** - Reverse proxy and static file server
- **Git** - Version control

## Architecture

The application uses a production-ready architecture:

```
Browser → Nginx (port 80) → Gunicorn (port 8000) → Django → PostgreSQL
```

**Services:**
- `db`: PostgreSQL 15 database
- `web`: Django application with Gunicorn (3 workers)
- `nginx`: Nginx reverse proxy serving static files and proxying to Gunicorn

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
   
   The `.env` file is already configured for Docker development:
   ```env
   DEBUG=True
   SECRET_KEY=django-insecure-change-this-in-production
   DB_NAME=landing_page_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. **Build and start containers**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Main application: **http://localhost**
   - Admin panel: **http://localhost/admin** (after creating superuser)

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
│   ├── settings.py       # Project settings (PostgreSQL only)
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
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
- Created `.env` file with PostgreSQL configuration
- Removed SQLite, using PostgreSQL exclusively

✅ **Docker Infrastructure**
- PostgreSQL 15 database with health checks
- Django application with Gunicorn WSGI server
- Nginx reverse proxy for production-like setup

✅ **Django Project**
- Initialized Django project "landing_page"
- Configured for PostgreSQL only
- Applied all initial migrations
- Static files collection configured

✅ **Production Ready**
- Nginx serving static files efficiently
- Gunicorn with multiple workers
- Shared volumes for static files
- Proper service dependencies and health checks

## License

This project is currently in development phase.
