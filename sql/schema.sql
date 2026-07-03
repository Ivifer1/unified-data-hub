-- ============================================================
-- Tablas para centralizar datos de Google Sheets, Notion y Trello
-- ============================================================

-- ─── Tabla: datos de Google Sheets (Ventas/Leads) ───
CREATE TABLE IF NOT EXISTS google_sheets_data (
    id          SERIAL PRIMARY KEY,
    source_id   VARCHAR(255),           -- ID original en Sheets
    name        VARCHAR(255),
    email       VARCHAR(255),
    phone       VARCHAR(100),
    status      VARCHAR(100),           -- lead, contactado, convertido
    amount      DECIMAL(10, 2),
    created_at  TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Tabla: datos de Notion (Proyectos/Tareas) ───
CREATE TABLE IF NOT EXISTS notion_data (
    id          SERIAL PRIMARY KEY,
    source_id   VARCHAR(255),           -- ID original en Notion
    title       VARCHAR(500),
    status      VARCHAR(100),           -- pendiente, en progreso, completado
    priority    VARCHAR(50),            -- alta, media, baja
    assignee    VARCHAR(255),
    due_date    DATE,
    created_at  TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Tabla: datos de Trello (Tareas/Tableros) ───
CREATE TABLE IF NOT EXISTS trello_data (
    id          SERIAL PRIMARY KEY,
    source_id   VARCHAR(255),           -- ID original en Trello
    card_name   VARCHAR(500),
    list_name   VARCHAR(255),           -- En qué lista está
    board_name  VARCHAR(255),
    member      VARCHAR(255),
    due_date    DATE,
    created_at  TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Tabla unificada (después de transformación) ───
CREATE TABLE IF NOT EXISTS unified_data (
    id              SERIAL PRIMARY KEY,
    source_platform VARCHAR(50) NOT NULL,   -- google_sheets, notion, trello
    source_id       VARCHAR(255),
    title           VARCHAR(500),
    status          VARCHAR(100),
    assignee        VARCHAR(255),
    priority        VARCHAR(50),
    amount          DECIMAL(10, 2),
    due_date        DATE,
    created_at      TIMESTAMP,
    imported_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Índices para consultas rápidas ───
CREATE INDEX IF NOT EXISTS idx_google_status ON google_sheets_data(status);
CREATE INDEX IF NOT EXISTS idx_notion_status ON notion_data(status);
CREATE INDEX IF NOT EXISTS idx_trello_list ON trello_data(list_name);
CREATE INDEX IF NOT EXISTS idx_unified_platform ON unified_data(source_platform);