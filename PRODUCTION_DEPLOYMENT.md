# Guide de Déploiement en Production

Ce guide vous accompagne étape par étape pour déployer cette application Django en production de manière sécurisée.

## ⚠️ Prérequis de Production

Avant de déployer, vous devez avoir :
- [ ] Un serveur (VPS, cloud instance, etc.) avec Docker installé
- [ ] Un nom de domaine configuré
- [ ] Certificats SSL/TLS (Let's Encrypt recommandé)
- [ ] Accès SSH au serveur
- [ ] Backup strategy définie

## 🔒 Étape 1 : Sécurisation de la Configuration

### 1.1 Créer un fichier `.env.production`

**Ne jamais commiter ce fichier !**

```bash
# Django Settings
DEBUG=False
SECRET_KEY=<générer-une-clé-secrète-forte-ici>
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com

# Database Settings
DB_NAME=landing_page_prod
DB_USER=landing_page_user
DB_PASSWORD=<mot-de-passe-très-fort-et-unique>
DB_HOST=db
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 1.2 Générer une SECRET_KEY sécurisée

```bash
# Sur votre serveur de production
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 1.3 Générer un mot de passe PostgreSQL fort

```bash
openssl rand -base64 32
```

## 🔧 Étape 2 : Modifications du Code pour la Production

### 2.1 Créer `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  web:
    build: .
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - backend

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - backend

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  backend:
    driver: bridge
```

### 2.2 Créer `nginx/nginx.prod.conf`

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name votredomaine.com www.votredomaine.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name votredomaine.com www.votredomaine.com;
    
    client_max_body_size 100M;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Serve static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Serve media files
    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy to Django/Gunicorn
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 2.3 Créer `nginx/Dockerfile.prod`

```dockerfile
FROM nginx:1.25-alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy production nginx configuration
COPY nginx.prod.conf /etc/nginx/conf.d/

# Create directory for certbot challenges
RUN mkdir -p /var/www/certbot

# Expose ports
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

### 2.4 Mettre à jour `landing_page/settings.py`

Ajouter ces configurations de sécurité :

```python
# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

## 🌐 Étape 3 : Configuration du Serveur

### 3.1 Préparer le serveur

```bash
# Se connecter au serveur
ssh user@votre-serveur.com

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo apt install docker-compose-plugin -y

# Créer les répertoires nécessaires
mkdir -p ~/landing_page
mkdir -p ~/landing_page/nginx/ssl
mkdir -p ~/landing_page/logs
```

### 3.2 Configurer le pare-feu

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## 🔐 Étape 4 : Obtenir des Certificats SSL

### Option A : Let's Encrypt avec Certbot (Recommandé)

```bash
# Installer Certbot
sudo apt install certbot -y

# Obtenir le certificat
sudo certbot certonly --standalone -d votredomaine.com -d www.votredomaine.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem ~/landing_page/nginx/ssl/
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem ~/landing_page/nginx/ssl/
sudo chown $USER:$USER ~/landing_page/nginx/ssl/*

# Configurer le renouvellement automatique
sudo certbot renew --dry-run
```

### Option B : Certificat auto-signé (Développement uniquement)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ~/landing_page/nginx/ssl/privkey.pem \
  -out ~/landing_page/nginx/ssl/fullchain.pem
```

## 🚀 Étape 5 : Déploiement

### 5.1 Transférer les fichiers

```bash
# Sur votre machine locale
rsync -avz --exclude 'venv' --exclude '.git' --exclude '__pycache__' \
  ./ user@votre-serveur.com:~/landing_page/
```

### 5.2 Configurer l'environnement

```bash
# Sur le serveur
cd ~/landing_page

# Créer le fichier .env.production avec vos valeurs sécurisées
nano .env.production
```

### 5.3 Lancer l'application

```bash
# Utiliser le fichier docker-compose de production
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Vérifier que tout fonctionne
docker-compose -f docker-compose.prod.yml ps

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5.4 Créer un superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 📊 Étape 6 : Monitoring et Maintenance

### 6.1 Configurer les backups automatiques

Créer un script de backup `backup.sh` :

```bash
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de backup
mkdir -p $BACKUP_DIR

# Backup de la base de données
docker-compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U landing_page_user landing_page_prod > \
  $BACKUP_DIR/db_backup_$DATE.sql

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql"
```

Ajouter au crontab :

```bash
# Backup quotidien à 2h du matin
crontab -e
# Ajouter :
0 2 * * * /home/user/landing_page/backup.sh
```

### 6.2 Monitoring avec logs

```bash
# Voir les logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Vérifier l'utilisation des ressources
docker stats
```

### 6.3 Mises à jour

```bash
# Sur votre machine locale, après avoir fait des modifications
git push origin main

# Sur le serveur
cd ~/landing_page
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Appliquer les migrations si nécessaire
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## ✅ Checklist de Déploiement

Avant de mettre en production, vérifiez :

- [ ] `DEBUG=False` dans `.env.production`
- [ ] `SECRET_KEY` unique et sécurisée générée
- [ ] Mots de passe PostgreSQL forts
- [ ] `ALLOWED_HOSTS` configuré avec votre domaine
- [ ] Certificats SSL installés et valides
- [ ] Pare-feu configuré (ports 80, 443, 22)
- [ ] Backups automatiques configurés
- [ ] DNS pointant vers votre serveur
- [ ] Logs configurés et accessibles
- [ ] Superuser créé
- [ ] Tests de l'application effectués
- [ ] Plan de rollback défini

## 🔄 Rollback en Cas de Problème

```bash
# Revenir à la version précédente
git checkout <commit-précédent>
docker-compose -f docker-compose.prod.yml up -d --build

# Restaurer un backup de base de données
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U landing_page_user landing_page_prod < backup.sql
```

## 📈 Améliorations Futures

- [ ] Ajouter un CDN pour les fichiers statiques
- [ ] Configurer Redis pour le cache
- [ ] Mettre en place un système de monitoring (Prometheus, Grafana)
- [ ] Configurer des alertes (email, Slack)
- [ ] Implémenter un CI/CD (GitHub Actions, GitLab CI)
- [ ] Ajouter des tests automatisés
- [ ] Configurer le load balancing si nécessaire
- [ ] Mettre en place une stratégie de scaling

## 🆘 Support et Dépannage

### Problèmes courants

**L'application ne démarre pas :**
```bash
docker-compose -f docker-compose.prod.yml logs web
```

**Erreur de connexion à la base de données :**
```bash
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml exec db psql -U landing_page_user -d landing_page_prod
```

**Certificats SSL expirés :**
```bash
sudo certbot renew
sudo cp /etc/letsencrypt/live/votredomaine.com/* ~/landing_page/nginx/ssl/
docker-compose -f docker-compose.prod.yml restart nginx
```

## 📚 Ressources Utiles

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security Headers](https://securityheaders.com/)
