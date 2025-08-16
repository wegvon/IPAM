# IP Subnet Management Platform (IPAM)

A comprehensive web application for network administrators to manage IP address spaces, subnet allocations, customer assignments, and network infrastructure.

## Features

- **Subnet Management**: Create, organize, and track IP subnets with hierarchical structure
- **Customer Management**: Handle individual and corporate customers
- **Assignment Tracking**: Manage subnet assignments with multi-currency pricing
- **Revenue Analytics**: Calculate revenue across USD, EUR, and TRY
- **Audit Logging**: Complete audit trail for all operations
- **Dashboard Analytics**: Real-time statistics and visualizations
- **Turkish UI**: Full Turkish language support

## Technology Stack

- **Backend**: Flask 3.1.1 (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5.3.2
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy 2.0

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd ipam-platform
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
flask db upgrade
flask seed-data
```

6. Run the application:
```bash
python main.py
```

### Docker Deployment

```bash
docker-compose up -d
```

### Coolify Deployment (Otomatik PostgreSQL ile)

**Tek tıkla deployment:**

1. **Coolify'da yeni app oluştur** (Docker Compose)
2. **Git repository'yi bağla**
3. **Environment variables ayarla:**
   ```bash
   SECRET_KEY=your-secret-key-here
   SESSION_SECRET=your-session-secret-here
   POSTGRES_PASSWORD=your-db-password-here
   ```
4. **Deploy et!** ✅

**PostgreSQL otomatik kurulur** - ekstra addon gerekmez!

## Default Credentials

After seeding:
- **Admin**: username: `admin`, password: `admin123`
- **Manager**: username: `manager`, password: `manager123`
- **Operator**: username: `operator`, password: `operator123`

## Documentation

See `PROJECT_DOCUMENTATION.md` for detailed technical documentation.

## License

Proprietary - All rights reserved
