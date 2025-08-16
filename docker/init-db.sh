#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- IPAM Platform PostgreSQL Initialization
    
    -- Set timezone to Istanbul
    SET timezone = 'Europe/Istanbul';
    
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Grant all privileges to ipam_user
    GRANT ALL PRIVILEGES ON DATABASE ipam_db TO ipam_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ipam_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ipam_user;
    
    -- Set default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ipam_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ipam_user;
    
    -- Log successful initialization
    \echo 'IPAM PostgreSQL database initialized successfully!'
EOSQL
