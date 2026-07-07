# n8n_workflows/

Carpeta para almacenar los workflows de n8n exportados en formato JSON.

## Como exportar un workflow desde n8n

1. Abre n8n en tu navegador: http://localhost:5678
2. Ve al workflow que quieres exportar
3. Haz clic en el menu (tres puntos) arriba a la derecha
4. Selecciona "Download" -> Guarda el archivo .json en esta carpeta
5. Renombra el archivo con un nombre descriptivo, por ejemplo:
   - fake_store_api_to_postgres.json
   - airtable_to_postgres.json
   - notion_crm_to_postgres.json

## Como importar un workflow

1. En n8n, haz clic en "Add Workflow"
2. Selecciona "Import from File"
3. Elige el archivo .json de esta carpeta
