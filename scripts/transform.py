"""
scripts/transform.py
Pipeline de transformacion de datos crudos -> limpios.
Lee de 'products', 'airtable_data', 'leads' y escribe en 'unified_data'.
La tabla unified_data ya existe (creada por schema.sql).

Fuentes:
- products      -> Fake Store API (catalogo)
- airtable_data -> Tareas operativas
- leads         -> Pipeline de ventas (Notion CRM)
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --------------------------------------------------
# CONFIGURACION DE CONEXION
# --------------------------------------------------
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "admin123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5434")
DB_NAME = os.getenv("POSTGRES_DB", "unified_hub")

CONN_STR = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(CONN_STR)

# --------------------------------------------------
# 1. EXTRACT - Leer datos crudos de las 3 fuentes
# --------------------------------------------------
print("Leyendo datos crudos de 3 fuentes...")

products_df = pd.read_sql("SELECT * FROM products", engine)
airtable_df = pd.read_sql("SELECT * FROM airtable_data", engine)
leads_df = pd.read_sql("SELECT * FROM leads", engine)

print(f"   -> {len(products_df)} productos (Fake Store API)")
print(f"   -> {len(airtable_df)} tareas (Airtable)")
print(f"   -> {len(leads_df)} leads (Notion CRM)")

total_raw = len(products_df) + len(airtable_df) + len(leads_df)
if total_raw == 0:
    print("No hay datos en ninguna tabla. Ejecuta primero los workflows de n8n.")
    exit(0)

# --------------------------------------------------
# 2. TRANSFORM - Normalizar y unificar
# --------------------------------------------------
print("Transformando y unificando datos...")

records = []

# 2.1 Transformar productos (Fake Store API)
if not products_df.empty:
    for _, row in products_df.iterrows():
        records.append({
            "source_platform": "products",
            "source_id": str(row["id"]),
            "title": str(row["title"]).strip().title() if pd.notna(row["title"]) else None,
            "status": str(row["category"]).strip().lower() if pd.notna(row["category"]) else None,
            "assignee": None,
            "priority": None,
            "amount": float(row["price"]) if pd.notna(row["price"]) else None,
            "due_date": None,
            "project_type": None,
            "created_at": row["imported_at"],
            "imported_at": row["imported_at"]
        })

# 2.2 Transformar tareas de Airtable
if not airtable_df.empty:
    for _, row in airtable_df.iterrows():
        records.append({
            "source_platform": "airtable",
            "source_id": str(row["source_id"]) if pd.notna(row["source_id"]) else None,
            "title": str(row["task"]).strip() if pd.notna(row["task"]) else None,
            "status": str(row["status"]).strip().lower() if pd.notna(row["status"]) else None,
            "assignee": str(row["assignee"]).strip() if pd.notna(row["assignee"]) else None,
            "priority": str(row["priority"]).strip().lower() if pd.notna(row["priority"]) else None,
            "amount": None,
            "due_date": row["due_date"] if pd.notna(row["due_date"]) else None,
            "project_type": None,
            "created_at": row["created_at"] if pd.notna(row["created_at"]) else row["imported_at"],
            "imported_at": row["imported_at"]
        })

# 2.3 Transformar leads de Notion (CRM)
if not leads_df.empty:
    for _, row in leads_df.iterrows():
        company = str(row["company"]).strip() if pd.notna(row["company"]) else "Sin empresa"
        contact = str(row["contact_name"]).strip() if pd.notna(row["contact_name"]) else "Sin contacto"

        records.append({
            "source_platform": "notion",
            "source_id": str(row["source_id"]) if pd.notna(row["source_id"]) else None,
            "title": f"{contact} @ {company}",
            "status": str(row["status"]).strip().lower() if pd.notna(row["status"]) else None,
            "assignee": str(row["assigned_to"]).strip() if pd.notna(row["assigned_to"]) else None,
            "priority": None,
            "amount": float(row["deal_value"]) if pd.notna(row["deal_value"]) else None,
            "due_date": row["last_contact"] if pd.notna(row["last_contact"]) else None,
            "project_type": str(row["source_channel"]).strip().lower() if pd.notna(row["source_channel"]) else None,
            "created_at": row["created_at"] if pd.notna(row["created_at"]) else row["imported_at"],
            "imported_at": row["imported_at"]
        })

unified_df = pd.DataFrame(records)

print(f"   -> {len(unified_df)} registros unificados en total.")

# --------------------------------------------------
# 3. LOAD - Limpiar e insertar en unified_data
# --------------------------------------------------
print("Guardando en 'unified_data'...")

with engine.connect() as conn:
    # Limpiar tabla unificada anterior (mantener estructura, borrar datos)
    conn.execute(text("TRUNCATE TABLE unified_data RESTART IDENTITY"))
    conn.commit()

# Insertar datos limpios
unified_df.to_sql(
    name="unified_data",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("Transformacion completada exitosamente.")
print(f"   -> Tabla 'unified_data' actualizada con {len(unified_df)} registros.")
print(f"      - Productos:   {len(unified_df[unified_df['source_platform'] == 'products'])}")
print(f"      - Airtable:    {len(unified_df[unified_df['source_platform'] == 'airtable'])}")
print(f"      - Notion CRM:  {len(unified_df[unified_df['source_platform'] == 'notion'])}")