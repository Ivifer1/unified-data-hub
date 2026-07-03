# 🔗 Unified Data Hub

> Pipeline de integración multi-plataforma con n8n, PostgreSQL y Streamlit. 
> Centraliza datos de Google Sheets, Notion y Trello en un solo dashboard.

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
- [Instalación](#instalación)
- [Configuración de Fuentes](#configuración-de-fuentes)
- [Uso](#uso)
- [Dashboard](#dashboard)
- [Tecnologías](#tecnologías)
- [Licencia](#licencia)

---

## Arquitectura

```
Google Sheets ──┐
Notion ─────────┼──▶ n8n ──▶ PostgreSQL ──▶ Python ──▶ Streamlit Dashboard
Trello ─────────┘         (Raw Data)      (Transform)   (Visualización)
```

**Flujo de datos:**

1. **Extract** — n8n se conecta a Google Sheets, Notion y Trello vía APIs
2. **Load** — n8n guarda los datos crudos en PostgreSQL
3. **Transform** — Python limpia, normaliza y enriquece los datos
4. **Visualize** — Streamlit muestra un dashboard unificado e interactivo

---

## Problema que Resuelve

Las empresas usan múltiples herramientas pero los datos quedan aislados:

| Antes | Después |
|-------|---------|
| Datos dispersos en 5+ plataformas | Un solo repositorio centralizado |
| Reportes manuales que toman horas | Dashboard automático en tiempo real |
| Errores por copiar y pegar datos | Pipeline automatizado sin intervención |
| Cada equipo ve solo su parte | Todos ven el panorama completo |

**Casos de uso:**
- Unificar leads de ventas, proyectos y tareas en un solo lugar
- Consolidar métricas de múltiples herramientas de trabajo
- Automatizar reportes ejecutivos sin intervención manual

---

## Estructura

```
unified-data-hub/
├── n8n_workflows/          # Flujos de n8n exportados (JSON)
├── scripts/
│   ├── __init__.py
│   ├── transform.py        # Limpieza y normalización
│   └── load.py             # Carga a PostgreSQL
├── sql/
│   └── schema.sql          # Esquema de tablas unificadas
├── data/
│   ├── raw/                # Datos crudos (backup)
│   └── processed/          # Datos limpios
├── docs/
│   └── architecture.md     # Decisiones técnicas
├── images/                 # Capturas de pantalla
├── README.md
├── docker-compose.yml      # PostgreSQL + n8n
├── requirements.txt        # Dependencias Python
└── app.py                # Dashboard Streamlit
```

---

## Prerrequisitos

| Herramienta | Versión | Enlace |
|-------------|---------|--------|
| Docker Desktop | 4.0+ | [Descargar](https://www.docker.com/products/docker-desktop/) |
| Python | 3.9+ | [Descargar](https://www.python.org/downloads/) |
| Git | 2.30+ | [Descargar](https://git-scm.com/) |
| Cuenta Google Cloud | — | Para API de Google Sheets |
| Cuenta Notion | — | Para integración |
| Cuenta Trello | — | Para API |

---

## Instalación

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

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| PostgreSQL | `5432` | Base de datos centralizada |
| n8n | `5678` | Editor de workflows |

### Paso 3: Acceder a n8n

- URL: http://localhost:5678
- Configurar cuenta inicial

### Paso 4: Instalar dependencias Python

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

---

## Configuración de Fuentes

### Google Sheets

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto → Habilitar Google Sheets API
3. Crear credenciales (Service Account)
4. Descargar JSON de credenciales
5. Configurar en n8n: **Google Sheets → PostgreSQL**

### Notion

1. Ir a [Notion Integrations](https://www.notion.so/my-integrations)
2. Crear nueva integración
3. Copiar **Internal Integration Token**
4. Compartir base de datos con la integración
5. Configurar en n8n: **Notion → PostgreSQL**

### Trello

1. Ir a [Trello Power-Ups](https://trello.com/power-ups/admin)
2. Generar **API Key** y **Token**
3. Configurar en n8n: **Trello → PostgreSQL**

---

## Uso

### Ejecutar transformaciones

```bash
python scripts/transform.py
```

### Ejecutar dashboard

```bash
streamlit run app.py
```

Acceso: http://localhost:8501

---

## Dashboard

El dashboard incluye:

- **Métricas clave**: Total de registros por fuente
- **Gráficos de barras**: Comparación entre plataformas
- **Tabla unificada**: Todos los datos filtrables
- **Actualización en tiempo real**: Se refresca automáticamente

---

## Tecnologías

| Tecnología | Propósito |
|------------|-----------|
| **n8n** | Orquestación visual de integraciones (no-code/low-code) |
| **PostgreSQL** | Base de datos relacional centralizada |
| **Python** | Lógica de transformación |
| **Pandas** | Limpieza y normalización de datos |
| **SQLAlchemy** | ORM para conexión a PostgreSQL |
| **Streamlit** | Dashboard interactivo |
| **Matplotlib** | Visualizaciones estáticas |
| **Docker** | Contenerización de servicios |
| **Git** | Control de versiones |

---

## Licencia

MIT License — Proyecto educativo para portafolio de Data Engineering.

---

## Autor

**Ivifer Pita** — [LinkedIn](https://www.linkedin.com/in/ivifer-pita-322527380/) — [GitHub](https://github.com/Ivifer1?tab=repositories)
