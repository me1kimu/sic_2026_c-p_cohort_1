"""
Dashboard de Gestión de Inventario y Demanda — Retail
Samsung Innovation Campus Chile 2026 — Grupo Seis

Pregunta de análisis:
    ¿Está el inventario calibrado frente a la demanda proyectada,
    y dónde y cuánto se desajusta entre riesgo de quiebre y exceso de inventario?
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# =========================================================
# 1. CONFIGURACIÓN GENERAL DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Dashboard Retail — Inventario y Demanda",
    layout="wide",
)

st.title("Dashboard de Gestión de Inventario y Demanda — Retail")

st.write(
    "Esta aplicación analiza si el **inventario** está bien dimensionado frente a la "
    "**demanda proyectada**, detectando riesgo de quiebre de stock y exceso de inventario. "
    "Es una herramienta de **diagnóstico**: revisa cómo se gestionó el inventario durante "
    "el período 2022-2024 para detectar dónde y cuánto se desajustó. "
    "Todos los indicadores y gráficos se actualizan según los filtros de la barra lateral."
)


# =========================================================
# 2. CARGA DE DATOS (con caché) Y COLUMNAS DERIVADAS
#    Calculamos aquí, una sola vez, las métricas que NO dependen
#    de los filtros (son a nivel de cada fila producto-tienda-día).
# =========================================================
@st.cache_data
def cargar_datos():
    # Ruta del CSV relativa a este archivo (app.py), no al directorio de ejecución.
    # Así funciona tanto en local como publicada en Streamlit Cloud desde una subcarpeta.
    ruta_csv = Path(__file__).parent / "data" / "retail_store_inventory.csv"
    df = pd.read_csv(ruta_csv)
    df["Date"] = pd.to_datetime(df["Date"])

    # Cobertura = cuántas veces el inventario cubre la demanda proyectada.
    # < 1  -> el inventario NO alcanza la demanda (riesgo de quiebre)
    # = 1  -> equilibrio
    # > 2  -> inventario holgado (más del doble de la demanda)
    # Evitamos dividir por cero o por demanda negativa.
    demanda_segura = df["Demand Forecast"].where(df["Demand Forecast"] > 0)
    df["Cobertura"] = df["Inventory Level"] / demanda_segura

    # Unidades que faltarían si la demanda supera al inventario (0 si no falta).
    df["Faltante"] = (df["Demand Forecast"] - df["Inventory Level"]).clip(lower=0)

    # Unidades de inventario por encima de la demanda (0 si no sobra).
    df["Exceso"] = (df["Inventory Level"] - df["Demand Forecast"]).clip(lower=0)

    # Banderas de las dos formas de desajuste.
    df["Riesgo"] = df["Demand Forecast"] > df["Inventory Level"]      # quiebre
    df["Sobrestock"] = df["Inventory Level"] > 2 * df["Demand Forecast"]  # exceso

    return df


df = cargar_datos()


# =========================================================
# 3. SIDEBAR - FILTROS
# =========================================================
st.sidebar.header("Filtros del dashboard")

categorias = st.sidebar.multiselect(
    "Categoría",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique()),
)

tiendas = st.sidebar.multiselect(
    "Tienda",
    options=sorted(df["Store ID"].unique()),
    default=sorted(df["Store ID"].unique()),
)

regiones = st.sidebar.multiselect(
    "Región",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)

fecha_min = df["Date"].min().date()
fecha_max = df["Date"].max().date()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

st.sidebar.caption(
    "Fuente: Retail Store Inventory Forecasting Dataset (Kaggle). "
    "Cada fila = un producto, en una tienda, en un día."
)


# =========================================================
# 4. APLICAR FILTROS
# =========================================================
df_filtrado = df[
    (df["Category"].isin(categorias))
    & (df["Store ID"].isin(tiendas))
    & (df["Region"].isin(regiones))
]

if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["Date"].dt.date >= fecha_inicio)
        & (df_filtrado["Date"].dt.date <= fecha_fin)
    ]

# Si los filtros dejan la tabla vacía, avisamos y detenemos la app.
if df_filtrado.empty:
    st.error("No hay datos disponibles con los filtros seleccionados. Ajusta los filtros.")
    st.stop()

# Trabajamos sobre una copia y agregamos una columna "Mes" (primer día del mes).
# Usamos to_period -> to_timestamp porque funciona en todas las versiones de pandas.
df_filtrado = df_filtrado.copy()
df_filtrado["Mes"] = df_filtrado["Date"].dt.to_period("M").dt.to_timestamp()


# =========================================================
# 5. CÁLCULOS PARA LOS KPIs (sobre los datos ya filtrados)
# =========================================================
ventas_totales = df_filtrado["Units Sold"].sum()
cobertura_mediana = df_filtrado["Cobertura"].median()
pct_riesgo = 100 * df_filtrado["Riesgo"].mean()
pct_sobrestock = 100 * df_filtrado["Sobrestock"].mean()

# Magnitudes tangibles del desajuste (en unidades acumuladas).
total_exceso = df_filtrado["Exceso"].sum()
total_faltante = df_filtrado["Faltante"].sum()
razon_exceso = (total_exceso / total_faltante) if total_faltante > 0 else float("nan")


# =========================================================
# 6. KPIs PRINCIPALES
# =========================================================
st.subheader("Indicadores principales")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ventas totales (unidades)",
    f"{ventas_totales:,.0f}",
    help="Suma de unidades vendidas en el período y filtros seleccionados.",
)
col2.metric(
    "Cobertura mediana",
    f"{cobertura_mediana:,.1f}x",
    help="Caso típico: la mitad de las situaciones cubre menos que esto y la otra mitad más. "
         "Usamos la mediana (no el promedio) porque es robusta a valores extremos. 1x = equilibrio.",
)
col3.metric(
    "% en riesgo de quiebre",
    f"{pct_riesgo:,.1f}%",
    help="Situaciones donde la demanda proyectada supera al inventario.",
)
col4.metric(
    "% con inventario holgado",
    f"{pct_sobrestock:,.1f}%",
    help="Situaciones donde el inventario supera el doble de la demanda proyectada.",
)


# =========================================================
# 7. RESUMEN EJECUTIVO DINÁMICO (lenguaje no técnico)
# =========================================================
st.subheader("Resumen ejecutivo")

st.info(
    f"El inventario cubre en mediana **{cobertura_mediana:.1f} veces** la demanda proyectada. "
    f"Solo el **{pct_riesgo:.1f}%** de los casos presenta riesgo de quiebre, mientras que el "
    f"**{pct_sobrestock:.1f}%** mantiene inventario holgado (más del doble de la demanda).\n\n"
    f"Además, en el período se registraron **{total_exceso:,.0f} unidades por sobre la demanda "
    f"proyectada** frente a solo **{total_faltante:,.0f} unidades faltantes**"
    + (f" (≈{razon_exceso:,.0f} a 1). " if total_faltante > 0 else ". ")
    + "El principal desajuste histórico no fue la falta de stock, sino la falta de calibración "
    "del inventario frente a la demanda."
)


# =========================================================
# 8. PESTAÑAS
# =========================================================
st.divider()

tab_inventario, tab_ventas, tab_promociones, tab_detalle = st.tabs(
    [
        "Inventario y demanda",
        "Ventas y demanda",
        "Reposición y promociones",
        "Datos filtrados",
    ]
)


# ---------------------------------------------------------
# TAB 1: INVENTARIO Y DEMANDA  (análisis principal)
# ---------------------------------------------------------
with tab_inventario:
    st.subheader("¿Está el inventario calibrado a la demanda?")

    # --- Gráfico A: evolución mensual de inventario vs demanda ---
    st.markdown("##### Evolución mensual: inventario vs demanda proyectada")
    st.write(
        "Agrupamos por mes para suavizar el ruido diario. Si las líneas se mantienen "
        "separadas, el inventario está sistemáticamente por encima (o por debajo) de la demanda."
    )

    serie_mensual = (
        df_filtrado.groupby("Mes", as_index=False)[["Inventory Level", "Demand Forecast"]]
        .mean()
    )
    serie_mensual_largo = serie_mensual.melt(
        id_vars="Mes",
        value_vars=["Inventory Level", "Demand Forecast"],
        var_name="Indicador",
        value_name="Promedio",
    )
    fig_serie = px.line(
        serie_mensual_largo,
        x="Mes",
        y="Promedio",
        color="Indicador",
        title="Inventario promedio vs demanda proyectada promedio (mensual)",
        markers=True,
    )
    fig_serie.update_layout(height=330, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_serie, width="stretch")
    st.caption("Promedios mensuales. El primer o último mes puede estar incompleto según el rango de fechas.")

    col_izq, col_der = st.columns(2)

    # --- Gráfico B: zonas de cobertura ---
    with col_izq:
        st.markdown("##### Zonas de cobertura")
        st.write(
            "Clasificamos cada situación según cuántas veces el inventario cubre la "
            "demanda: riesgo (<1x), normal (1-2x), holgado (2-5x) y muy alto (>5x)."
        )
        orden_zonas = ["Riesgo (<1x)", "Normal (1-2x)", "Holgado (2-5x)", "Muy alto (>5x)"]
        zonas = pd.cut(
            df_filtrado["Cobertura"],
            bins=[-np.inf, 1, 2, 5, np.inf],
            labels=orden_zonas,
        )
        zona_df = (
            zonas.value_counts(normalize=True)
            .reindex(orden_zonas)
            .fillna(0)
            .mul(100)
            .reset_index()
        )
        zona_df.columns = ["Zona", "Porcentaje"]
        fig_zonas = px.bar(
            zona_df, x="Zona", y="Porcentaje", color="Zona",
            text_auto=".1f", title="% de situaciones por zona de cobertura",
            color_discrete_map={
                "Riesgo (<1x)": "#e74c3c", "Normal (1-2x)": "#2ecc71",
                "Holgado (2-5x)": "#f39c12", "Muy alto (>5x)": "#c0392b",
            },
        )
        fig_zonas.update_layout(
            height=300, showlegend=False,
            xaxis_title="", yaxis_title="% de situaciones",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_zonas, width="stretch")

    # --- Gráfico C: inventario vs demanda por categoría ---
    with col_der:
        st.markdown("##### Inventario vs demanda por categoría")
        st.write(
            "Compara el promedio de inventario y demanda en cada categoría. "
            "Permite ver si el desajuste es general o de una categoría puntual."
        )
        inv_dem_cat = (
            df_filtrado.groupby("Category", as_index=False)
            .agg({"Inventory Level": "mean", "Demand Forecast": "mean"})
        )
        inv_dem_cat_largo = inv_dem_cat.melt(
            id_vars="Category",
            value_vars=["Inventory Level", "Demand Forecast"],
            var_name="Indicador",
            value_name="Promedio",
        )
        fig_cat = px.bar(
            inv_dem_cat_largo,
            x="Promedio", y="Category", color="Indicador",
            orientation="h", barmode="group",
            title="Promedio por categoría",
        )
        fig_cat.update_layout(
            height=300, bargap=0.35, margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_cat, width="stretch")

    # --- Tablero de diagnóstico: peores situaciones del período ---
    st.markdown("##### Tablero de diagnóstico: peores situaciones del período")
    st.write(
        "Estas son las situaciones donde el desajuste fue más severo en 2022-2024. "
        "Sirven para auditar dónde falló la gestión (no es una lista de tareas de hoy: "
        "en un sistema en vivo, esta misma lógica sobre datos actuales marcaría qué reponer ahora)."
    )

    vista = st.radio(
        "¿Qué desajuste quieres revisar?",
        ["Mayor déficit (riesgo de quiebre)", "Mayor exceso (sobre-stock)"],
        horizontal=True,
    )

    if vista.startswith("Mayor déficit"):
        en_riesgo = df_filtrado[df_filtrado["Riesgo"]].copy()
        if en_riesgo.empty:
            st.success("No hay situaciones en riesgo de quiebre con los filtros actuales.")
        else:
            def severidad_falta(cob):
                # cob = cobertura (inventario/demanda); aquí siempre < 1
                if cob < 0.5:
                    return "Severo"
                elif cob < 0.8:
                    return "Moderado"
                else:
                    return "Leve"

            en_riesgo["Severidad"] = en_riesgo["Cobertura"].apply(severidad_falta)
            tabla = (
                en_riesgo.sort_values("Faltante", ascending=False)
                .head(10)
                .loc[:, ["Date", "Store ID", "Product ID", "Category", "Region",
                         "Inventory Level", "Demand Forecast", "Faltante", "Severidad"]]
                .copy()
            )
            tabla["Date"] = tabla["Date"].dt.strftime("%Y-%m-%d")
            colores = {"Severo": "#f8d7da", "Moderado": "#fff3cd", "Leve": "#d1e7dd"}

            def color_fila(fila):
                return [f"background-color: {colores.get(fila['Severidad'], '')}"] * len(fila)

            st.dataframe(
                tabla.style.apply(color_fila, axis=1),
                width="stretch", hide_index=True,
            )
    else:
        con_exceso = df_filtrado[df_filtrado["Exceso"] > 0].copy()
        if con_exceso.empty:
            st.info("No hay situaciones con exceso de inventario con los filtros actuales.")
        else:
            tabla = (
                con_exceso.sort_values("Exceso", ascending=False)
                .head(10)
                .loc[:, ["Date", "Store ID", "Product ID", "Category", "Region",
                         "Inventory Level", "Demand Forecast", "Exceso"]]
                .copy()
            )
            tabla["Date"] = tabla["Date"].dt.strftime("%Y-%m-%d")
            st.dataframe(tabla, width="stretch", hide_index=True)


# ---------------------------------------------------------
# TAB 2: VENTAS Y DEMANDA
# ---------------------------------------------------------
with tab_ventas:
    st.subheader("Ventas y demanda proyectada")

    corr_vd = df_filtrado["Units Sold"].corr(df_filtrado["Demand Forecast"])
    st.write(
        "Las ventas dan escala al negocio. Además comparamos las ventas reales con la "
        "demanda proyectada: si el pronóstico acompaña bien a las ventas, el problema no "
        "está en el forecast, sino en cómo se gestiona el inventario frente a esa demanda."
    )
    st.metric(
        "Correlación ventas vs demanda proyectada",
        f"{corr_vd:.2f}",
        help="Cercano a 1 significa que la demanda proyectada sigue casi perfectamente a las ventas reales.",
    )

    col_a, col_b = st.columns(2)

    with col_a:
        ventas_categoria = (
            df_filtrado.groupby("Category", as_index=False)["Units Sold"]
            .sum()
            .sort_values("Units Sold", ascending=True)
        )
        fig_vc = px.bar(
            ventas_categoria, x="Units Sold", y="Category",
            orientation="h", title="Ventas totales por categoría", text_auto=True,
        )
        fig_vc.update_layout(height=320, bargap=0.4, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_vc, width="stretch")

    with col_b:
        # Promedio mensual (no suma) para no distorsionar si el último mes está incompleto.
        vd_mes = (
            df_filtrado.groupby("Mes", as_index=False)
            .agg({"Units Sold": "mean", "Demand Forecast": "mean"})
        )
        vd_mes_largo = vd_mes.melt(
            id_vars="Mes",
            value_vars=["Units Sold", "Demand Forecast"],
            var_name="Serie", value_name="Promedio",
        )
        fig_vm = px.line(
            vd_mes_largo, x="Mes", y="Promedio", color="Serie",
            title="Ventas reales vs demanda proyectada (promedio mensual)", markers=True,
        )
        fig_vm.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_vm, width="stretch")
        st.caption("Promedio por registro. El primer o último mes puede estar incompleto según el rango de fechas.")


# ---------------------------------------------------------
# TAB 3: REPOSICIÓN Y PROMOCIONES
# ---------------------------------------------------------
with tab_promociones:
    # --- Reposición: ¿responde a la necesidad? (análisis principal de la pestaña) ---
    st.subheader("¿La reposición responde a la necesidad?")
    st.write(
        "Comparamos las unidades ordenadas (reposición) en situaciones de riesgo de quiebre "
        "frente a situaciones de sobre-stock. Si la reposición fuera inteligente, se ordenaría "
        "más cuando falta stock y menos cuando sobra."
    )

    ordenado_riesgo = df_filtrado.loc[df_filtrado["Riesgo"], "Units Ordered"].mean()
    ordenado_exceso = df_filtrado.loc[df_filtrado["Sobrestock"], "Units Ordered"].mean()

    col_r1, col_r2 = st.columns([1.3, 1])

    with col_r1:
        rep_df = pd.DataFrame(
            {
                "Situación": ["Riesgo de quiebre (falta stock)", "Sobre-stock (sobra stock)"],
                "Unidades ordenadas (promedio)": [ordenado_riesgo, ordenado_exceso],
            }
        )
        fig_rep = px.bar(
            rep_df, x="Situación", y="Unidades ordenadas (promedio)",
            title="Reposición promedio según la necesidad", text_auto=".1f",
            color="Situación",
            color_discrete_map={
                "Riesgo de quiebre (falta stock)": "#e74c3c",
                "Sobre-stock (sobra stock)": "#f39c12",
            },
        )
        fig_rep.update_layout(
            height=320, bargap=0.5, showlegend=False,
            xaxis_title="", margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_rep, width="stretch")

    with col_r2:
        st.markdown("### Lectura del resultado")
        if pd.notna(ordenado_riesgo) and pd.notna(ordenado_exceso):
            dif_rep = ordenado_riesgo - ordenado_exceso
            st.metric("Diferencia de reposición", f"{dif_rep:+.1f} unidades")
            if abs(dif_rep) < 5:
                st.warning(
                    "Se ordena prácticamente **lo mismo** cuando falta stock que cuando sobra: "
                    "la reposición **no responde a la necesidad** de inventario."
                )
            elif dif_rep > 0:
                st.success("Se ordena más cuando falta stock: la reposición responde a la necesidad.")
            else:
                st.warning("Se ordena más cuando ya sobra stock: la reposición va en contra de la necesidad.")
        else:
            st.info("No hay suficientes casos de ambos tipos con los filtros actuales.")

    st.divider()

    # --- Promociones (hallazgo secundario) ---
    st.subheader("Impacto de promociones o feriados")
    st.write(
        "Como hallazgo secundario, comparamos las ventas promedio con y sin promoción/feriado, "
        "y calculamos el 'uplift' (variación porcentual)."
    )

    df_promo = df_filtrado.copy()
    df_promo["Estado promoción"] = df_promo["Holiday/Promotion"].map(
        {0: "Sin promoción/feriado", 1: "Con promoción/feriado"}
    )
    promo_ventas = (
        df_promo.groupby("Estado promoción", as_index=False)["Units Sold"].mean()
    )

    col_p1, col_p2 = st.columns([1.3, 1])

    with col_p1:
        fig_promo = px.bar(
            promo_ventas, x="Estado promoción", y="Units Sold",
            title="Ventas promedio según promoción o feriado", text_auto=".1f",
        )
        fig_promo.update_layout(
            height=320, bargap=0.5, margin=dict(l=20, r=20, t=50, b=20),
            yaxis_title="Unidades vendidas promedio", xaxis_title="",
        )
        st.plotly_chart(fig_promo, width="stretch")

    with col_p2:
        st.markdown("### Lectura del resultado")
        mapa = dict(zip(promo_ventas["Estado promoción"], promo_ventas["Units Sold"]))
        con = mapa.get("Con promoción/feriado")
        sin = mapa.get("Sin promoción/feriado")

        if con is not None and sin is not None and sin != 0:
            uplift = 100 * (con - sin) / sin
            st.metric("Uplift de promoción", f"{uplift:+.1f}%")
            if abs(uplift) < 2:
                st.info(
                    "Las promociones y feriados **no muestran un aumento relevante** "
                    "en las ventas promedio en este dataset."
                )
            elif uplift > 0:
                st.success("Las situaciones con promoción venden en promedio más.")
            else:
                st.warning("Las situaciones con promoción venden en promedio menos.")
        else:
            st.info("No hay datos suficientes de ambos grupos con los filtros actuales.")


# ---------------------------------------------------------
# TAB 4: DATOS FILTRADOS
# ---------------------------------------------------------
with tab_detalle:
    st.subheader("Datos filtrados")
    st.write(f"Filas disponibles después de aplicar filtros: **{df_filtrado.shape[0]:,}**")

    # Mostramos solo las columnas originales del dataset (sin columnas internas
    # calculadas como Cobertura, Faltante, Exceso, Mes, etc.).
    columnas_originales = [
        "Date", "Store ID", "Product ID", "Category", "Region",
        "Inventory Level", "Units Sold", "Units Ordered", "Demand Forecast",
        "Price", "Discount", "Weather Condition", "Holiday/Promotion",
        "Competitor Pricing", "Seasonality",
    ]
    with st.expander("Ver tabla de datos filtrados (primeras 100 filas)"):
        tabla_filtrada = df_filtrado.head(100)[columnas_originales].copy()
        tabla_filtrada["Date"] = tabla_filtrada["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(tabla_filtrada, width="stretch")

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar datos filtrados (CSV)",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv",
    )