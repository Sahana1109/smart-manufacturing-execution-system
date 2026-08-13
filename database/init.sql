-- SmartMES Database Initialization Script
-- Executed automatically on first container startup

-- Create extensions if required
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Database setting optimizations for development
ALTER DATABASE smartmes_db SET timezone TO 'UTC';
