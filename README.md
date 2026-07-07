# Unified Data Hub

> Pipeline de integracion multi-plataforma con n8n, PostgreSQL y Streamlit.
> Centraliza datos de APIs externas (Fake Store API, Airtable, Notion) en un solo dashboard.

![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Problema que Resuelve](#problema-que-resuelve)
- [Estructura](#estructura)
- [Prerrequisitos](#prerrequisitos)
- [Instalacion](#instalacion)
- [Configuracion de Fuentes](#configuracion-de-fuentes)
- [Pipeline de Datos](#pipeline-de-datos)
- [Dashboard](#dashboard)
- [Tecnologias](#tecnologias)
- [Licencia](#licencia)

---

## Arquitectura

```
Fake Store API --> n8n --> PostgreSQL (raw) --> Python --> PostgreSQL (unified) --> Streamlit
Airtable     --> n8n --> PostgreSQL (raw) --> transform.py --> PostgreSQL (unified) --> Streamlit
Notion CRM   --> n8n --> PostgreSQL (raw) -->              --> PostgreSQL (unified) --> Streamlit
```

**Flujo de datos (ELT):**

1. **Extract** - n8n se conecta a APIs externas (Fake Store API, Airtable, Notion)
2. **Load** - n8n guarda los datos crudos en PostgreSQL (products, airtable_data, leads)
3. **Transform** - Python limpia, normaliza y unifica los datos en unified_data (scripts/transform.py)
4. **Visualize** - Streamlit muestra un dashboard unificado e interactivo

---

## Problema que Resuelve

Las empresas usan multiples herramientas pero los datos quedan aislados:

| Antes | Despues |
|-------|---------|
| Datos dispersos en 3+ plataformas | Un solo repositorio centralizado |
| Reportes manuales que toman horas | Dashboard automatico en tiempo real |
| Errores por copiar y pegar datos | Pipeline automatizado sin intervencion |
| Cada equipo ve solo su parte | Todos ven el panorama completo |

**Casos de uso:**
- Unificar catalogo de productos, tareas operativas y pipeline de ventas en un solo lugar
- Consolidar metricas de multiples herramientas de trabajo
- Automatizar reportes ejecutivos sin intervencion manual

---

## Estructura

```
unified-data-hub/
|-- n8n_workflows/          # Workflows de n8n exportados (JSON)
|   |-- README.md           # Guia de exportacion/importacion
|-- scripts/
|   |-- transform.py        # Transformacion y unificacion de datos
|-- sql/
|   |-- schema.sql          # Esquema de tablas (products, airtable_data, leads, unified_data)
|-- docs/
|   |-- architecture.md     # Decisiones tecnicas del proyecto
|-- README.md
|-- docker-compose.yml      # PostgreSQL + n8n
|-- requirements.txt        # Dependencias Python
|-- app.py                  # Dashboard Streamlit
```

---

## Prerrequisitos

| Herramienta | Version | Enlace |
|-------------|---------|--------|
| Docker Desktop | 4.0+ | [Descargar](https://www.docker.com/products/docker-desktop/) |
| Python | 3.9+ | [Descargar](https://www.python.org/downloads/) |
| Git | 2.30+ | [Descargar](https://git-scm.com/) |
| Cuenta Airtable | - | Para integracion |
| Cuenta Notion | - | Para CRM |

---

## Instalacion

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/unified-data-hub.git
cd unified-data-hub
```

### Paso 2: Levantar servicios con Docker

```bash
docker-compose up -d
```

Servicios que se crean:

| Servicio | Puerto | Descripcion |
|----------|--------|-------------|
| PostgreSQL | 5434 | Base de datos centralizada (mapeado a localhost) |
| n8n | 5678 | Editor de workflows |

### Paso 3: Crear entorno virtual Python

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Paso 4: Crear tablas en PostgreSQL

El archivo sql/schema.sql se monta automaticamente en Docker y se ejecuta al iniciar el contenedor por primera vez.

Si necesitas recrear las tablas manualmente:

```bash
docker exec -i unified_postgres psql -U admin -d unified_hub < sql/schema.sql
```

---

## Configuracion de Fuentes

### Fake Store API (Demo / Pruebas)

1. En n8n, crea un workflow con un nodo HTTP Request
2. URL: https://fakestoreapi.com/products
3. Conecta a un nodo PostgreSQL -> Inserta en tabla products
4. Mapea los campos: title, price, category, description, image, rating.rate, rating.count

### Airtable (Tareas operativas)

1. Crear base en Airtable llamada "Data Hub Tasks"
2. Configurar campos: Task, Status, Priority, Assignee, Due Date
3. Obtener Personal Access Token en airtable.com/create/tokens
4. Obtener Base ID y Table ID de la URL de la base
5. En n8n: Airtable -> PostgreSQL (tabla airtable_data)

### Notion CRM (Pipeline de ventas)

1. Crear integracion en notion.so/my-integrations
2. Crear base "Pipeline de Ventas" con campos: Company, Contact, Email, Status, Deal Value, Source, Assigned To, Last Contact
3. Conectar integracion a la base
4. En n8n: Notion -> PostgreSQL (tabla leads)

---

## Pipeline de Datos

### 1. Ingesta con n8n

Ejecutar los workflows de n8n para insertar datos crudos en las tablas respectivas.

### 2. Transformacion con Python

```bash
python scripts/transform.py
```

Esto:
- Lee de products, airtable_data, leads (datos crudos)
- Limpia, normaliza y unifica los datos
- Inserta en unified_data (datos unificados)

### 3. Visualizacion con Streamlit

```bash
streamlit run app.py
```

Acceso: http://localhost:8501

---

## Dashboard

El dashboard incluye:

- **Metricas clave**: Total de registros por fuente, precio promedio, valor de pipeline
- **Graficos interactivos**: Precio por categoria, embudo de ventas, tareas por estado
- **Tablas filtrables**: Productos, tareas, leads con filtros por plataforma
- **Vista unificada**: Todos los datos en una sola tabla
- **Auto-refresh**: Opcion de recarga automatica cada 30 segundos

---

## Tecnologias

| Tecnologia | Proposito |
|------------|-----------|
| n8n | Orquestacion visual de integraciones (no-code/low-code) |
| PostgreSQL | Base de datos relacional centralizada |
| Python | Logica de transformacion y limpieza |
| Pandas | Manipulacion y normalizacion de datos |
| SQLAlchemy | ORM para conexion a PostgreSQL |
| Streamlit | Dashboard interactivo |
| Matplotlib | Visualizaciones estaticas |
| Docker | Contenerizacion de servicios |
| Git | Control de versiones |

---

## Licencia

MIT License - Proyecto educativo para portafolio de Data Engineering.

---

## Autor

Ivifer Pita - [LinkedIn](https://www.linkedin.com/in/ivifer-pita-322527380/) - [GitHub](https://github.com/Ivifer1?tab=repositories)
