-- ============================================================
-- Unified Data Hub — Esquema de base de datos
-- PostgreSQL 15
-- 3 fuentes: Fake Store API (Productos) | Airtable (Tareas) | Notion (CRM/Leads)
-- ============================================================

-- Fuente 1: Fake Store API — Catálogo de productos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    price DECIMAL(10,2),
    category VARCHAR(100),
    description TEXT,
    image VARCHAR(500),
    rating_rate DECIMAL(3,2),
    rating_count INTEGER,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente 2: Airtable — Tareas operativas del equipo
CREATE TABLE IF NOT EXISTS airtable_data (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(255),
    task VARCHAR(500),
    status VARCHAR(100),
    priority VARCHAR(50),
    assignee VARCHAR(255),
    due_date DATE,
    created_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente 3: Notion — Pipeline de ventas (CRM)
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(255),
    company VARCHAR(255),
    contact_name VARCHAR(255),
    email VARCHAR(255),
    status VARCHAR(100),
    deal_value DECIMAL(12,2),
    source_channel VARCHAR(100),
    assigned_to VARCHAR(255),
    last_contact DATE,
    created_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla unificada (output de transform.py)
-- Combina productos + tareas + leads
CREATE TABLE IF NOT EXISTS unified_data (
    id SERIAL PRIMARY KEY,
    source_platform VARCHAR(50) NOT NULL,
    source_id VARCHAR(255),
    title VARCHAR(500),
    status VARCHAR(100),
    assignee VARCHAR(255),
    priority VARCHAR(50),
    amount DECIMAL(15, 2),
    due_date DATE,
    project_type VARCHAR(100),
    created_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_airtable_status ON airtable_data(status);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_channel ON leads(source_channel);
CREATE INDEX IF NOT EXISTS idx_unified_platform ON unified_data(source_platform);
CREATE INDEX IF NOT EXISTS idx_unified_status ON unified_data(status);