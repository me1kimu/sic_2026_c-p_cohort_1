import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general de la página
st.set_page_config(
    page_title="Dashboard Retail",
    layout="wide"
)

# Título principal
st.title("Dashboard de Ventas e Inventario Retail")

st.write(
    """
    Esta aplicación permite analizar ventas, inventario y demanda proyectada
    en el sector retail mediante filtros interactivos y métricas clave.
    """
)

# Cargar datos con caché
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/retail_store_inventory.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = cargar_datos()

# =========================
# SIDEBAR - FILTROS
# =========================

st.sidebar.header("Filtros del dashboard")

categorias = st.sidebar.multiselect(
    "Categoría",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

regiones = st.sidebar.multiselect(
    "Región",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

estacionalidades = st.sidebar.multiselect(
    "Estacionalidad",
    options=sorted(df["Seasonality"].unique()),
    default=sorted(df["Seasonality"].unique())
)

# Filtro extra de fechas
fecha_min = df["Date"].min().date()
fecha_max = df["Date"].max().date()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# =========================
# APLICAR FILTROS
# =========================

df_filtrado = df[
    (df["Category"].isin(categorias)) &
    (df["Region"].isin(regiones)) &
    (df["Seasonality"].isin(estacionalidades))
]

# Aplicar filtro de fechas
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["Date"].dt.date >= fecha_inicio) &
        (df_filtrado["Date"].dt.date <= fecha_fin)
    ]

# =========================
# KPIs PRINCIPALES
# =========================

st.subheader("Indicadores principales")

ventas_totales = df_filtrado["Units Sold"].sum()
inventario_promedio = df_filtrado["Inventory Level"].mean()
demanda_promedio = df_filtrado["Demand Forecast"].mean()

# Definimos riesgo de quiebre:
# cuando la demanda proyectada es mayor que el inventario disponible
df_riesgo = df_filtrado[df_filtrado["Demand Forecast"] > df_filtrado["Inventory Level"]]
productos_en_riesgo = df_riesgo["Product ID"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas totales", f"{ventas_totales:,.0f}")
col2.metric("Inventario promedio", f"{inventario_promedio:,.1f}")
col3.metric("Productos en riesgo", productos_en_riesgo)
col4.metric("Demanda proyectada promedio", f"{demanda_promedio:,.1f}")

# =========================
# LECTURA EJECUTIVA
# =========================

st.subheader("Lectura rápida del estado actual")

if df_filtrado.empty:
    st.error("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

categoria_top = (
    df_filtrado
    .groupby("Category")["Units Sold"]
    .sum()
    .idxmax()
)

region_top = (
    df_filtrado
    .groupby("Region")["Units Sold"]
    .sum()
    .idxmax()
)

if productos_en_riesgo > 0:
    st.warning(
        f"Se detectan **{productos_en_riesgo} productos en riesgo de quiebre**. "
        f"La categoría con mayor volumen de ventas es **{categoria_top}** y la región con mayor demanda es **{region_top}**."
    )
else:
    st.success(
        f"No se detectan productos en riesgo bajo los filtros actuales. "
        f"La categoría con mayor volumen de ventas es **{categoria_top}** y la región con mayor demanda es **{region_top}**."
    )


# =========================
# VISUALIZACIONES ORDENADAS
# =========================

# =========================
# VISUALIZACIONES ORDENADAS
# =========================

st.divider()

tab_ventas, tab_inventario, tab_promociones, tab_detalle = st.tabs(
    [
        "Ventas",
        "Inventario y demanda",
        "Promociones",
        "Datos filtrados"
    ]
)

# =========================
# TAB 1: VENTAS
# =========================

with tab_ventas:
    st.subheader("Análisis de ventas")

    st.write(
        "Esta sección muestra cómo se distribuyen las ventas según categoría, región y evolución temporal."
    )

    col_a, col_b = st.columns(2)

    # Ventas por categoría - gráfico horizontal
    ventas_categoria = (
        df_filtrado
        .groupby("Category", as_index=False)["Units Sold"]
        .sum()
        .sort_values("Units Sold", ascending=True)
    )

    fig_ventas_categoria = px.bar(
        ventas_categoria,
        x="Units Sold",
        y="Category",
        orientation="h",
        title="Ventas totales por categoría",
        text_auto=True
    )

    fig_ventas_categoria.update_layout(
    height=280,
    bargap=0.55,
    margin=dict(l=20, r=20, t=50, b=20)
)
    col_a.plotly_chart(fig_ventas_categoria, width="stretch")

    # Ventas por región - gráfico horizontal
    ventas_region = (
        df_filtrado
        .groupby("Region", as_index=False)["Units Sold"]
        .sum()
        .sort_values("Units Sold", ascending=True)
    )

    fig_region = px.bar(
        ventas_region,
        x="Units Sold",
        y="Region",
        orientation="h",
        title="Ventas totales por región",
        text_auto=True
    )

    fig_region.update_layout(
    height=330,
    margin=dict(l=20, r=20, t=50, b=20)
)

    col_b.plotly_chart(fig_region, width="stretch")

    # Evolución temporal de ventas
    ventas_tiempo = (
        df_filtrado
        .groupby("Date", as_index=False)["Units Sold"]
        .sum()
    )

    fig_tiempo = px.line(
        ventas_tiempo,
        x="Date",
        y="Units Sold",
        title="Evolución temporal de las ventas"
    )

    fig_tiempo.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig_tiempo, width="stretch")


# =========================
# TAB 2: INVENTARIO Y DEMANDA
# =========================

with tab_inventario:
    st.subheader("Inventario vs demanda proyectada")

    st.write(
        "Esta sección compara el inventario disponible con la demanda proyectada. "
        "Cuando la demanda proyectada supera al inventario, puede existir riesgo de quiebre de stock."
    )

    inventario_demanda = (
        df_filtrado
        .groupby("Category", as_index=False)
        .agg({
            "Inventory Level": "mean",
            "Demand Forecast": "mean"
        })
    )

    inventario_demanda_largo = inventario_demanda.melt(
        id_vars="Category",
        value_vars=["Inventory Level", "Demand Forecast"],
        var_name="Indicador",
        value_name="Valor promedio"
    )

    fig_inv_demanda = px.bar(
        inventario_demanda_largo,
        x="Valor promedio",
        y="Category",
        color="Indicador",
        orientation="h",
        barmode="group",
        title="Inventario promedio vs demanda proyectada promedio por categoría"
    )

    fig_inv_demanda.update_layout(
    height=300,
    bargap=0.45,
    margin=dict(l=20, r=20, t=50, b=20)
)

    st.plotly_chart(fig_inv_demanda, width="stretch")

    st.markdown("### Top 10 registros con mayor riesgo")

    productos_riesgo = (
        df_filtrado
        .assign(Risk_Score=df_filtrado["Demand Forecast"] / df_filtrado["Inventory Level"])
        .sort_values("Risk_Score", ascending=False)
        .head(10)
    )

    tabla_riesgo = productos_riesgo[
    [
        "Date",
        "Store ID",
        "Product ID",
        "Category",
        "Region",
        "Inventory Level",
        "Demand Forecast",
        "Risk_Score"
    ]
].copy()

tabla_riesgo["Date"] = tabla_riesgo["Date"].dt.strftime("%Y-%m-%d")
tabla_riesgo["Risk_Score"] = tabla_riesgo["Risk_Score"].round(2)

st.dataframe(tabla_riesgo, width="stretch")

# =========================
# TAB 3: PROMOCIONES
# =========================

with tab_promociones:
    st.subheader("Impacto de promociones o feriados")

    st.write(
        "Esta sección compara las ventas promedio entre registros con promoción/feriado "
        "y registros sin promoción/feriado."
    )

    df_promo = df_filtrado.copy()

    df_promo["Estado promoción"] = df_promo["Holiday/Promotion"].map({
        0: "Sin promoción/feriado",
        1: "Con promoción/feriado"
    })

    promo_ventas = (
        df_promo
        .groupby("Estado promoción", as_index=False)["Units Sold"]
        .mean()
    )

    col_promo_1, col_promo_2 = st.columns([1.2, 1])

    fig_promo = px.bar(
        promo_ventas,
        x="Estado promoción",
        y="Units Sold",
        title="Ventas promedio según promoción o feriado",
        text_auto=".1f"
    )

    fig_promo.update_layout(
        height=300,
        bargap=0.55,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Unidades vendidas promedio",
        xaxis_title=""
    )

    col_promo_1.plotly_chart(fig_promo, width="stretch")

    if len(promo_ventas) == 2:
        venta_sin_promo = promo_ventas.loc[
            promo_ventas["Estado promoción"] == "Sin promoción/feriado",
            "Units Sold"
        ].values[0]

        venta_con_promo = promo_ventas.loc[
            promo_ventas["Estado promoción"] == "Con promoción/feriado",
            "Units Sold"
        ].values[0]

        diferencia = venta_con_promo - venta_sin_promo

        with col_promo_2:
            st.markdown("### Lectura del resultado")

            st.metric(
                "Diferencia promedio",
                f"{diferencia:.1f} unidades"
            )

            if diferencia > 0:
                st.success(
                    "Los registros con promoción o feriado presentan una venta promedio mayor."
                )
            elif diferencia < 0:
                st.warning(
                    "Los registros con promoción o feriado presentan una venta promedio levemente menor."
                )
            else:
                st.info(
                    "No se observa diferencia promedio entre ambos grupos."
                )

# =========================
# TAB 4: DATOS FILTRADOS
# =========================

with tab_detalle:
    st.subheader("Datos filtrados")

    st.write(
        f"Filas disponibles después de aplicar filtros: **{df_filtrado.shape[0]:,}**"
    )

    with st.expander("Ver tabla de datos filtrados"):
        tabla_filtrada = df_filtrado.head(100).copy()
        tabla_filtrada["Date"] = tabla_filtrada["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(tabla_filtrada, width="stretch")