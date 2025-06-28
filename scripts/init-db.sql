-- T-Beauty Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database (already done by POSTGRES_DB env var)
-- CREATE DATABASE tbeauty;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create a sample admin user (optional - can be done via API)
-- Note: This is just a placeholder. Actual user creation should be done via the API
-- to ensure proper password hashing

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'T-Beauty database initialized successfully';
    RAISE NOTICE 'Database: tbeauty';
    RAISE NOTICE 'User: tbeauty_user';
    RAISE NOTICE 'Timezone: UTC';
END $$;