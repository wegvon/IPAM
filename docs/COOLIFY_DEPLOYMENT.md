# IPAM Platform - Coolify Deployment Guide

This guide will help you deploy the IPAM Platform on Coolify.

## Prerequisites

- A Coolify instance set up and running
- A Git repository containing the IPAM Platform code
- PostgreSQL database addon available in Coolify

## Step 1: Create Application in Coolify

1. Login to your Coolify dashboard
2. Click "New" → "Application"
3. Choose "Public Repository" and enter your Git repository URL
4. Select the branch (usually `main` or `master`)
5. Choose "Docker" as the build pack
6. Set application name as "ipam-platform"

## Step 2: Configure Environment Variables

In Coolify application settings, add the following environment variables:

### Required Variables

```bash
# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=production

# Security (IMPORTANT: Change these!)
SECRET_KEY=your-super-secret-key-change-this-in-production
SESSION_SECRET=another-super-secret-key-change-this-too

# Application Settings
APP_NAME=IPAM Platform
APP_PORT=5000
APP_HOST=0.0.0.0

# Locale Settings
DEFAULT_LOCALE=tr_TR
TIMEZONE=Europe/Istanbul
```

### Database Configuration

The `DATABASE_URL` will be automatically provided by Coolify when you attach a PostgreSQL addon (see Step 3).

### Optional Variables

```bash
# Exchange Rate API (for currency conversion)
EXCHANGE_RATE_API_KEY=your-api-key-here
EXCHANGE_RATE_API_URL=https://api.exchangerate-api.com/v4/latest/

# Logging
LOG_TO_STDOUT=1
LOG_LEVEL=INFO
```

## Step 3: Add PostgreSQL Database

1. In your application settings, go to "Addons"
2. Click "Add Addon" → "PostgreSQL"
3. Choose the latest PostgreSQL version (15 recommended)
4. Set database name: `ipam_db`
5. Set username: `ipam_user`
6. Generate a secure password
7. Deploy the addon

Once deployed, Coolify will automatically set the `DATABASE_URL` environment variable.

## Step 4: Configure Build and Deploy

### Build Settings

- **Build Command**: Auto-detected from Dockerfile
- **Start Command**: Auto-detected from Dockerfile
- **Port**: 5000 (already configured in Dockerfile)

### Health Check

The application includes a health check endpoint at `/health`. Coolify will automatically use the Docker HEALTHCHECK instruction.

## Step 5: Deploy

1. Click "Deploy" in your Coolify application dashboard
2. Monitor the build logs for any errors
3. Once deployed, the application will be available at your assigned URL

## Step 6: Initialize Database

After successful deployment, you need to initialize the database with the schema and seed data:

1. Open a terminal/console in your Coolify application
2. Run the following commands:

```bash
# Create database tables
flask db upgrade

# Seed initial data (users, sample data)
flask seed-data
```

## Step 7: Access the Application

- Navigate to your application URL provided by Coolify
- Login with the default credentials:
  - **Admin**: `admin` / `admin123`
  - **Manager**: `manager` / `manager123`
  - **Operator**: `operator` / `operator123`

**IMPORTANT**: Change these default passwords immediately after first login!

## Post-Deployment Configuration

### Security Hardening

1. **Change Default Passwords**: Update all default user passwords
2. **Update Secret Keys**: Ensure you've changed `SECRET_KEY` and `SESSION_SECRET`
3. **Review User Permissions**: Remove unused demo users
4. **Enable HTTPS**: Configure SSL certificate in Coolify

### Backup Strategy

1. **Database Backups**: Configure regular PostgreSQL backups in Coolify
2. **File Backups**: The application is stateless, so database backups are sufficient
3. **Configuration Backup**: Keep a copy of your environment variables

### Monitoring

1. **Application Logs**: Monitor via Coolify logs interface
2. **Health Checks**: The `/health` endpoint provides basic status
3. **Database Monitoring**: Use Coolify's PostgreSQL monitoring features

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check environment variables are set correctly
   - Verify DATABASE_URL is properly configured
   - Review build logs for Python dependency errors

2. **Database connection errors**
   - Ensure PostgreSQL addon is running
   - Check DATABASE_URL format
   - Verify network connectivity between app and database

3. **Login issues**
   - Run `flask seed-data` to create initial users
   - Check SECRET_KEY is set and consistent
   - Verify database tables were created

### Log Access

Access application logs through:
1. Coolify dashboard → Your App → Logs
2. Or via CLI: `coolify logs <app-name>`

### Database Access

Access PostgreSQL database:
1. Coolify dashboard → PostgreSQL Addon → Connect
2. Use provided connection details with your preferred PostgreSQL client

## Scaling Considerations

### Horizontal Scaling

- The application is designed to be stateless
- Multiple instances can be deployed behind a load balancer
- Ensure session storage is handled appropriately for multiple instances

### Vertical Scaling

- Monitor memory usage and CPU utilization
- Adjust container resources in Coolify as needed
- PostgreSQL may need additional resources as data grows

## Updates and Maintenance

### Application Updates

1. Push changes to your Git repository
2. Trigger deployment in Coolify
3. Monitor logs during update
4. Run database migrations if needed: `flask db upgrade`

### Database Maintenance

1. Regular vacuum and analyze operations
2. Monitor disk usage and performance
3. Keep PostgreSQL version updated
4. Implement backup rotation strategy

## Security Best Practices

1. **Use HTTPS**: Always enable SSL/TLS in production
2. **Environment Variables**: Never commit secrets to version control
3. **Database Security**: Use strong passwords and network isolation
4. **Regular Updates**: Keep dependencies and OS packages updated
5. **Access Control**: Limit database and application access
6. **Monitoring**: Implement logging and monitoring for security events

---

For additional support or questions about deployment, please refer to:
- Coolify documentation: https://coolify.io/docs
- IPAM Platform documentation in this repository
- Create an issue in the project repository for bugs or feature requests
