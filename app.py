import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# --------------------------------------------------
# CONFIGURACION DE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Unified Data Hub - Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# CONEXION A POSTGRESQL (Docker)
# --------------------------------------------------
@st.cache_resource
def get_engine():
    DB_USER = os.getenv("POSTGRES_USER", "admin")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "admin123")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5434")
    DB_NAME = os.getenv("POSTGRES_DB", "unified_hub")
    conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)


def load_data(query):
    """Carga datos desde PostgreSQL."""
    engine = get_engine()
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error al conectar con PostgreSQL: {e}")
        return pd.DataFrame()


# --------------------------------------------------
# TITULO Y REFRESH
# --------------------------------------------------
st.title("Unified Data Hub")
st.caption("3 fuentes -> n8n -> PostgreSQL -> Python -> Streamlit | Productos | Tareas | CRM")

st_autorefresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
if st_autorefresh:
    st.markdown("<meta http-equiv=\"refresh\" content=\"30\" />", unsafe_allow_html=True)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
products_df = load_data("SELECT * FROM products ORDER BY imported_at DESC")
airtable_df = load_data("SELECT * FROM airtable_data ORDER BY imported_at DESC")
leads_df = load_data("SELECT * FROM leads ORDER BY imported_at DESC")
unified_df = load_data("SELECT * FROM unified_data ORDER BY imported_at DESC")

if unified_df.empty:
    st.warning("No hay datos en 'unified_data'. Ejecuta primero: python scripts/transform.py")
    st.stop()

# --------------------------------------------------
# SIDEBAR - FILTROS GLOBALES
# --------------------------------------------------
st.sidebar.header("Filtros Globales")

platforms = ["Todas"] + sorted(unified_df["source_platform"].dropna().unique().tolist())
selected_platform = st.sidebar.selectbox("Plataforma", platforms)

filtered_unified = unified_df.copy()
if selected_platform != "Todas":
    filtered_unified = filtered_unified[filtered_unified["source_platform"] == selected_platform]

st.sidebar.markdown("---")
st.sidebar.metric("Registros totales", len(unified_df))
st.sidebar.metric("Registros filtrados", len(filtered_unified))

# --------------------------------------------------
# SECCION 1: KPIs UNIFICADOS
# --------------------------------------------------
st.subheader("Metricas Unificadas")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Registros", len(unified_df))
prod_count = len(unified_df[unified_df["source_platform"] == "products"])
air_count = len(unified_df[unified_df["source_platform"] == "airtable"])
leads_count = len(unified_df[unified_df["source_platform"] == "notion"])
col2.metric("Productos", prod_count)
col3.metric("Tareas Airtable", air_count)
col4.metric("Leads Notion", leads_count)

st.markdown("---")

# --------------------------------------------------
# SECCION 2: PRODUCTOS (Fake Store API)
# --------------------------------------------------
with st.expander("Productos - Fake Store API", expanded=True):
    if not products_df.empty:
        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
        pcol1.metric("Total", len(products_df))
        pcol2.metric("Precio Promedio", f"${products_df['price'].mean():.2f}")
        pcol3.metric("Rating Promedio", f"{products_df['rating_rate'].mean():.2f}")
        pcol4.metric("Precio Max", f"${products_df['price'].max():.2f}")

        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("**Precio promedio por categoria**")
            avg_price = products_df.groupby("category")["price"].mean().sort_values(ascending=True)
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = plt.cm.Spectral_r(range(len(avg_price)))
            avg_price.plot(kind="barh", ax=ax, color=colors, edgecolor="black", linewidth=0.5)
            ax.set_xlabel("Precio ($)")
            ax.set_ylabel("")
            ax.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        with fig_col2:
            st.markdown("**Distribucion de Ratings**")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(products_df["rating_rate"].dropna(), bins=[0,1,2,3,4,5], color="#4CAF50", edgecolor="black", alpha=0.8)
            ax.set_xlabel("Rating")
            ax.set_ylabel("Cantidad")
            ax.set_xticks([0.5,1.5,2.5,3.5,4.5])
            ax.set_xticklabels(["0-1","1-2","2-3","3-4","4-5"])
            ax.grid(axis="y", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        st.dataframe(
            products_df[["id","title","price","category","rating_rate","rating_count","imported_at"]],
            use_container_width=True, hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "title": st.column_config.TextColumn("Producto", width="large"),
                "price": st.column_config.NumberColumn("Precio", format="$%.2f"),
                "category": st.column_config.TextColumn("Categoria"),
                "rating_rate": st.column_config.NumberColumn("Rating", format="%.2f"),
                "rating_count": st.column_config.NumberColumn("Reviews"),
                "imported_at": st.column_config.DatetimeColumn("Importado", format="DD/MM/YYYY HH:mm"),
            }
        )
    else:
        st.info("No hay datos de productos. Ejecuta el workflow de Fake Store API en n8n.")

st.markdown("---")

# --------------------------------------------------
# SECCION 3: TAREAS (Airtable)
# --------------------------------------------------
with st.expander("Tareas - Airtable", expanded=True):
    if not airtable_df.empty:
        acol1, acol2, acol3, acol4 = st.columns(4)
        acol1.metric("Total", len(airtable_df))
        a_status = airtable_df["status"].value_counts()
        acol2.metric("En Progreso", a_status.get("En Progreso", 0))
        acol3.metric("Completadas", a_status.get("Completado", 0))
        acol4.metric("Backlog", a_status.get("Backlog", 0))

        afig1, afig2 = st.columns(2)
        with afig1:
            st.markdown("**Tareas por estado**")
            fig, ax = plt.subplots(figsize=(6, 4))
            status_order = ["Backlog", "En Progreso", "Completado"]
            a_status_ordered = a_status.reindex(status_order, fill_value=0)
            colors = {"Backlog": "#9E9E9E", "En Progreso": "#FF9800", "Completado": "#4CAF50"}
            a_status_ordered.plot(kind="bar", ax=ax, color=[colors.get(s, "#2196F3") for s in a_status_ordered.index],
                                  edgecolor="black", linewidth=0.5)
            ax.set_xlabel("")
            ax.set_ylabel("Cantidad")
            ax.set_xticklabels(a_status_ordered.index, rotation=0)
            ax.grid(axis="y", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        with afig2:
            st.markdown("**Tareas por prioridad**")
            fig, ax = plt.subplots(figsize=(6, 4))
            a_priority = airtable_df["priority"].value_counts()
            priority_order = ["Alta", "Media", "Baja"]
            a_priority_ordered = a_priority.reindex(priority_order, fill_value=0)
            colors = {"Alta": "#F44336", "Media": "#FF9800", "Baja": "#4CAF50"}
            a_priority_ordered.plot(kind="bar", ax=ax, color=[colors.get(p, "#2196F3") for p in a_priority_ordered.index],
                                    edgecolor="black", linewidth=0.5)
            ax.set_xlabel("")
            ax.set_ylabel("Cantidad")
            ax.set_xticklabels(a_priority_ordered.index, rotation=0)
            ax.grid(axis="y", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        st.dataframe(
            airtable_df[["id","task","status","priority","assignee","due_date","imported_at"]],
            use_container_width=True, hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "task": st.column_config.TextColumn("Tarea", width="large"),
                "status": st.column_config.TextColumn("Estado"),
                "priority": st.column_config.TextColumn("Prioridad"),
                "assignee": st.column_config.TextColumn("Asignado"),
                "due_date": st.column_config.DateColumn("Fecha limite", format="DD/MM/YYYY"),
                "imported_at": st.column_config.DatetimeColumn("Importado", format="DD/MM/YYYY HH:mm"),
            }
        )
    else:
        st.info("No hay datos de Airtable. Ejecuta el workflow de Airtable en n8n.")

st.markdown("---")

# --------------------------------------------------
# SECCION 4: CRM - LEADS (Notion)
# --------------------------------------------------
with st.expander("CRM - Pipeline de Ventas (Notion)", expanded=True):
    if not leads_df.empty:
        lcol1, lcol2, lcol3, lcol4 = st.columns(4)
        lcol1.metric("Total Leads", len(leads_df))

        total_pipeline = leads_df["deal_value"].sum()
        lcol2.metric("Valor Pipeline", f"${total_pipeline:,.0f}")

        avg_deal = leads_df["deal_value"].mean()
        lcol3.metric("Deal Promedio", f"${avg_deal:,.0f}")

        l_status = leads_df["status"].value_counts()
        lcol4.metric("En Negociacion", l_status.get("Negociacion", 0))

        st.markdown("---")

        lfig1, lfig2 = st.columns(2)

        with lfig1:
            st.markdown("**Embudo de ventas (leads por estado)**")
            fig, ax = plt.subplots(figsize=(6, 4))
            funnel_order = ["Nuevo", "Contactado", "Propuesta", "Negociacion", "Cerrado"]
            l_status_ordered = l_status.reindex(funnel_order, fill_value=0)
            colors = {"Nuevo": "#2196F3", "Contactado": "#FF9800", "Propuesta": "#9C27B0", 
                      "Negociacion": "#F44336", "Cerrado": "#4CAF50"}
            l_status_ordered.plot(kind="barh", ax=ax, 
                color=[colors.get(s, "#2196F3") for s in l_status_ordered.index],
                edgecolor="black", linewidth=0.5)
            ax.set_xlabel("Cantidad de leads")
            ax.set_ylabel("")
            ax.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        with lfig2:
            st.markdown("**Leads por canal de origen**")
            fig, ax = plt.subplots(figsize=(6, 4))
            channel_counts = leads_df["source_channel"].value_counts()
            channel_counts.plot(kind="barh", ax=ax, color="#4CAF50", edgecolor="black", linewidth=0.5)
            ax.set_xlabel("Cantidad")
            ax.set_ylabel("")
            ax.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

        st.markdown("**Top 5 oportunidades por valor**")
        top_deals = leads_df.nlargest(5, "deal_value")[["company", "contact_name", "deal_value", "status", "assigned_to"]].sort_values("deal_value", ascending=True)
        fig, ax = plt.subplots(figsize=(8, 3))
        y_pos = range(len(top_deals))
        ax.barh(y_pos, top_deals["deal_value"], color="#FF5722", edgecolor="black", linewidth=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['company'][:15]}..." if len(row['company']) > 15 else row['company'] for _, row in top_deals.iterrows()], fontsize=9)
        ax.set_xlabel("Deal Value ($)")
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("**Tabla de Leads**")
        st.dataframe(
            leads_df[["id","company","contact_name","email","status","deal_value","source_channel","assigned_to","last_contact","imported_at"]],
            use_container_width=True, hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "company": st.column_config.TextColumn("Empresa", width="medium"),
                "contact_name": st.column_config.TextColumn("Contacto", width="medium"),
                "email": st.column_config.TextColumn("Email"),
                "status": st.column_config.TextColumn("Estado"),
                "deal_value": st.column_config.NumberColumn("Deal Value", format="$%.2f"),
                "source_channel": st.column_config.TextColumn("Canal"),
                "assigned_to": st.column_config.TextColumn("Asignado"),
                "last_contact": st.column_config.DateColumn("Ultimo contacto", format="DD/MM/YYYY"),
                "imported_at": st.column_config.DatetimeColumn("Importado", format="DD/MM/YYYY HH:mm"),
            }
        )
    else:
        st.info("No hay datos de CRM. Ejecuta el workflow de Notion en n8n.")

st.markdown("---")

# --------------------------------------------------
# SECCION 5: VISTA UNIFICADA
# --------------------------------------------------
st.subheader("Vista Unificada (Todas las fuentes)")

st.dataframe(
    filtered_unified[["source_platform","title","status","assignee","priority","amount","due_date","project_type","imported_at"]],
    use_container_width=True, hide_index=True,
    column_config={
        "source_platform": st.column_config.TextColumn("Fuente"),
        "title": st.column_config.TextColumn("Titulo"),
        "status": st.column_config.TextColumn("Estado"),
        "assignee": st.column_config.TextColumn("Asignado"),
        "priority": st.column_config.TextColumn("Prioridad"),
        "amount": st.column_config.NumberColumn("Monto", format="$%.2f"),
        "due_date": st.column_config.DateColumn("Fecha limite", format="DD/MM/YYYY"),
        "project_type": st.column_config.TextColumn("Canal / Tipo"),
        "imported_at": st.column_config.DatetimeColumn("Importado", format="DD/MM/YYYY HH:mm"),
    }
)

st.markdown("---")
st.caption("Desarrollado por Ivifer Pita | Unified Data Hub")