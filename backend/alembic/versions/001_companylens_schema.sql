-- COMPANYLENS Production PostgreSQL Schema Migration
-- Matches Section 19 and Section 46 Indexes

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1. DATA SOURCES
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- OFFICIAL, GOVERNMENT OPEN DATA, AUTHORIZED API, LICENSED PROVIDER
    provider TEXT,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    requires_auth BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. COMPANIES
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    legal_name TEXT NOT NULL,
    trade_name TEXT,
    cin TEXT UNIQUE,
    company_status TEXT DEFAULT 'ACTIVE',
    company_type TEXT,
    company_class TEXT,
    company_category TEXT,
    incorporation_date DATE,
    registered_state TEXT,
    roc TEXT,
    registered_address TEXT,
    authorized_capital NUMERIC(18, 2),
    paid_up_capital NUMERIC(18, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_companies_cin ON companies (cin);
CREATE INDEX IF NOT EXISTS idx_companies_legal_name ON companies (legal_name);
CREATE INDEX IF NOT EXISTS idx_companies_legal_name_trgm ON companies USING gin (legal_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_registered_state ON companies (registered_state);

-- 3. IDENTIFIERS (PAN, CIN, GSTIN Graph)
CREATE TABLE IF NOT EXISTS identifiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- PAN, CIN, GSTIN
    normalized_value TEXT NOT NULL,
    value_hash TEXT NOT NULL, -- SHA-256 (Never store unmasked raw PAN in open logs)
    is_primary BOOLEAN DEFAULT FALSE,
    source_id UUID REFERENCES data_sources(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_identifiers_company_id ON identifiers (company_id);
CREATE INDEX IF NOT EXISTS idx_identifiers_normalized_val ON identifiers (normalized_value);
CREATE INDEX IF NOT EXISTS idx_identifiers_value_hash ON identifiers (value_hash);

-- 4. GST REGISTRATIONS
CREATE TABLE IF NOT EXISTS gst_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    gstin VARCHAR(15) UNIQUE NOT NULL,
    state TEXT NOT NULL,
    registration_date DATE,
    status TEXT DEFAULT 'ACTIVE',
    cancellation_date DATE,
    taxpayer_type TEXT DEFAULT 'Regular',
    business_constitution TEXT,
    centre_jurisdiction TEXT,
    state_jurisdiction TEXT,
    principal_place_of_business TEXT,
    additional_places JSONB DEFAULT '[]'::jsonb,
    nature_of_business JSONB DEFAULT '[]'::jsonb,
    source_id UUID REFERENCES data_sources(id),
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gst_registrations_gstin ON gst_registrations (gstin);
CREATE INDEX IF NOT EXISTS idx_gst_registrations_state ON gst_registrations (state);
CREATE INDEX IF NOT EXISTS idx_gst_registrations_company_id ON gst_registrations (company_id);

-- 5. DIRECTORS
CREATE TABLE IF NOT EXISTS directors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    designation TEXT NOT NULL,
    appointment_date DATE,
    cessation_date DATE,
    source_id UUID REFERENCES data_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_directors_company_id ON directors (company_id);

-- 6. FINANCIAL YEARS
CREATE TABLE IF NOT EXISTS financial_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    financial_year TEXT NOT NULL,
    revenue NUMERIC(18, 2),
    profit_loss NUMERIC(18, 2),
    net_worth NUMERIC(18, 2),
    assets NUMERIC(18, 2),
    liabilities NUMERIC(18, 2),
    cash_flow NUMERIC(18, 2),
    paid_up_capital NUMERIC(18, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    source_id UUID REFERENCES data_sources(id),
    source_type TEXT DEFAULT 'Licensed Financial Data Provider',
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_financial_years_company_id ON financial_years (company_id);

-- 7. FILINGS
CREATE TABLE IF NOT EXISTS filings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    filing_type TEXT NOT NULL,
    financial_year TEXT,
    filing_date DATE,
    status TEXT DEFAULT 'Approved',
    metadata_json JSONB DEFAULT '{}'::jsonb,
    source_id UUID REFERENCES data_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_filings_company_id ON filings (company_id);

-- 8. COMPANY EVENTS (Change Detection & Timeline)
CREATE TABLE IF NOT EXISTS company_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_date DATE NOT NULL,
    description TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    source_id UUID REFERENCES data_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_company_events_company_id ON company_events (company_id);

-- 9. DATA RECORDS (Provenance & Conflict Storage)
CREATE TABLE IF NOT EXISTS data_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    source_id UUID REFERENCES data_sources(id),
    entity_type TEXT NOT NULL,
    field_name TEXT NOT NULL,
    field_value JSONB NOT NULL,
    verification_status TEXT DEFAULT 'SOURCE_REPORTED',
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_data_records_company_field ON data_records (company_id, field_name);

-- 10. SEARCH HISTORY
CREATE TABLE IF NOT EXISTS search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    identifier_type VARCHAR(20) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    result_company_id UUID REFERENCES companies(id) ON DELETE SET NULL
);

-- 11. WATCHLISTS
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_company ON watchlists (user_id, company_id);

-- 12. API LOGS
CREATE TABLE IF NOT EXISTS api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    provider VARCHAR(100),
    status_code INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    error_code VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
