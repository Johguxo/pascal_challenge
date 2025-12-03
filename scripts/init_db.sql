-- Pascal Real Estate Database Initialization
-- This script runs automatically when the PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create message_type enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_type') THEN
        CREATE TYPE public.message_type AS ENUM ('human', 'ai-assistant');
    END IF;
END$$;

-- Note: Tables are created by SQLAlchemy models
-- This script only handles extensions and custom types that need to exist first

-- Create indexes for vector similarity search (run after tables are created)
-- These will be created by a separate migration or manually

-- Useful queries for debugging:

-- Check if pgvector is installed:
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check tables:
-- \dt

-- Check enum types:
-- SELECT typname, enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid;

