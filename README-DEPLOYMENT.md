# IPAM Platform - Coolify Deployment

## Deployment Information

- **Application Name**: IPAM Platform
- **Server IP**: 185.85.238.230
- **Application Port**: 5000
- **Access URL**: http://185.85.238.230:5000

## Services

### Web Application
- **Port**: 5000
- **Framework**: Flask
- **Server**: Gunicorn
- **Health Check**: /health endpoint

### Database
- **Type**: PostgreSQL 15
- **Database**: ipam_db
- **User**: ipam_user
- **Port**: 5432 (internal)

## Environment Variables

The application uses the following environment variables:

- `FLASK_ENV=production`
- `FLASK_APP=main.py`
- `DATABASE_URL=postgresql://ipam_user:ipam_secure_2024@db:5432/ipam_db`
- `SECRET_KEY=ipam-super-secret-key-2024-production-185-85-238-230`
- `APP_HOST=0.0.0.0`
- `APP_PORT=5000`

## Access Information

After successful deployment, you can access the application at:

**URL**: http://185.85.238.230:5000

## Health Check

The application provides a health check endpoint:
- **URL**: http://185.85.238.230:5000/health
- **Response**: `{"status": "healthy", "service": "IPAM Platform"}`

## Troubleshooting

If the application is not accessible:

1. Check if containers are running
2. Verify port 5000 is open on the server
3. Check application logs in Coolify dashboard
4. Verify database connection is healthy
