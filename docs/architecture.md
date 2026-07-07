# Decisiones Tecnicas - Unified Data Hub

> Documento de arquitectura y justificacion de decisiones tecnicas del proyecto.

---

## 1. Arquitectura General: ELT vs ETL

**Decision:** Usar ELT (Extract -> Load -> Transform) en lugar de ETL tradicional.

**Justificacion:**
- PostgreSQL es lo suficientemente potente para almacenar datos crudos temporalmente.
- Python (Pandas) ofrece mayor flexibilidad para transformaciones complejas que n8n puro.
- Permite re-ejecutar transformaciones sin volver a extraer datos de las APIs.
- Facilita debugging: podemos inspeccionar tablas raw vs unified.

```
APIs --> n8n --> PostgreSQL (raw) --> Python/Pandas --> PostgreSQL (unified) --> Streamlit
```

---

## 2. Por que PostgreSQL sobre SQLite o MySQL

| Criterio | PostgreSQL | SQLite | MySQL |
|----------|------------|--------|-------|
| Concurrencia | Alta | Limitada | Alta |
| Tipos avanzados | JSONB, Arrays | Basicos | Parcial |
| Docker-friendly | Oficial | Ligero | Oficial |
| Ecosistema Data | Mejor soporte | Limitado | Moderado |

**Decision:** PostgreSQL 15 por su robustez, soporte de JSONB (para futuras extensiones) y mejor integracion con el ecosistema de datos.

---

## 3. Esquema de Datos: Tablas Raw + Tabla Unified

**Decision:** Separar datos crudos (products, airtable_data, leads) de datos unificados (unified_data).

**Justificacion:**
- **Auditabilidad:** Siempre podemos comparar antes/despues de la transformacion.
- **Reprocesamiento:** Si cambiamos la logica de transformacion, no necesitamos re-extraer de las APIs.
- **Resiliencia:** Un error en transformacion no afecta los datos crudos originales.
- **Escalabilidad:** Facilita agregar nuevas fuentes con su propia tabla raw.

### Tablas Raw
Almacenan exactamente lo que devuelven las APIs. Sin modificaciones.

### Tabla unified_data (Transformed)
Normaliza campos de diferentes fuentes en un esquema comun:
- source_platform: Identifica la fuente (products, airtable, notion)
- title: Nombre normalizado del item
- status: Estado normalizado
- assignee: Persona asignada
- amount: Valor numerico (precio o deal value)
- due_date: Fecha relevante

---

## 4. Por que n8n sobre Airflow o Prefect

**Contexto:** Proyecto de portafolio, necesita ser visual y facil de entender.

| Criterio | n8n | Airflow | Prefect |
|----------|-----|---------|---------|
| Curva de aprendizaje | Baja | Alta | Media |
| UI Visual | Drag-and-drop | Limitada | Limitada |
| Self-hosted | Facil | Complejo | Complejo |
| Ideal para portafolio | Si | Overkill | Overkill |

**Decision:** n8n por su interfaz visual, facilidad de despliegue con Docker y excelente presentacion en portafolio.

---

## 5. Por que Streamlit sobre Dash o Power BI

| Criterio | Streamlit | Dash | Power BI |
|----------|-----------|------|----------|
| Codigo Python puro | Si | Si | No |
| Open Source | Si | Si | No |
| Despliegue sencillo | Si | Moderado | Licencia |
| Ideal para demos | Si | Moderado | Moderado |

**Decision:** Streamlit porque permite un dashboard 100% Python, facil de versionar en Git y desplegar sin licencias.

---

## 6. Manejo de IDs y Claves Primarias

**Problema:** Las APIs externas tienen sus propios IDs, pero necesitamos un ID interno unico.

**Solucion:**
- id SERIAL PRIMARY KEY en PostgreSQL: ID interno autogenerado.
- source_id VARCHAR: Guarda el ID original de la API (para trazabilidad).
- En n8n: NO enviamos id, dejamos que PostgreSQL lo genere automaticamente.

**Leccion aprendida:** En el primer intento se envio id=0 desde n8n, causando violacion de unicidad. Se resolvio eliminando el campo id del mapeo de n8n.

---

## 7. Docker Compose: Puerto 5434 para PostgreSQL

**Decision:** Mapear PostgreSQL al puerto 5434 en lugar del estandar 5432.

**Justificacion:**
- Evitar conflictos si el usuario ya tiene PostgreSQL instalado localmente (puerto 5432 ocupado).
- El puerto interno del contenedor sigue siendo 5432, solo el host usa 5434.

```yaml
ports:
  - "5434:5432"
```

---

## 8. Separacion de Responsabilidades

**Decision:** Mantener transform.py como script independiente del dashboard.

**Justificacion:**
- El proceso ETL no debe mezclarse con la visualizacion.
- Permite ejecutar transformaciones por separado (CI/CD, schedules).
- Facilita testing unitario de la logica de transformacion.
- El dashboard solo lee datos ya procesados.

---

## 9. Futuras Mejoras

1. **Schedules en n8n:** Automatizar la ejecucion de workflows cada hora/dia.
2. **Tests:** Agregar pytest para validar transformaciones.
3. **CI/CD:** GitHub Actions para validar schema.sql y dependencias.
4. **Variables de entorno:** Mover credenciales a .env (actualmente hardcodeadas para demo).
5. **Nuevas fuentes:** Agregar Google Sheets, Slack, o APIs propietarias.
