# Sistema de Diagnóstico de Inventario y Demanda para Retail

Dashboard interactivo que analiza si el **inventario** de una operación retail estuvo bien
dimensionado frente a la **demanda proyectada** durante el período 2022-2024, detectando
riesgo de quiebre de stock, exceso de inventario y fallas en la reposición. Está construido
en Streamlit y orientado a una audiencia no técnica.

Proyecto final del **Samsung Innovation Campus Chile 2026 — Cohort 1**, curso de Código y
Programación (C&P). Equipo: Grupo Seis / Equipo 6.

---

## Pregunta de análisis

> ¿Está el inventario calibrado frente a la demanda proyectada, y dónde y cuánto se desajusta
> entre riesgo de quiebre (falta de stock) y exceso de inventario?

Como pregunta secundaria, evaluamos si las promociones influyen en las ventas y si la
reposición responde a la necesidad real de inventario.

**¿Quién se beneficia?** Un encargado de gestión de inventario o de reposición, que puede usar
este diagnóstico para identificar dónde la operación inmovilizó stock o arriesgó quiebres, y
ajustar su política a futuro.

---

## Hallazgos principales

1. **El inventario casi siempre supera a la demanda.** La cobertura mediana es de **1,9x**
   (el inventario cubre casi el doble de la demanda proyectada). Solo el **3,5%** de las
   situaciones presenta riesgo de quiebre, mientras que el **48%** mantiene inventario holgado.

2. **El desajuste es por exceso, no por falta.** En el período se registraron millones de
   unidades por sobre la demanda proyectada frente a apenas miles de unidades faltantes. La
   falta de stock fue marginal; el problema fue la falta de calibración del inventario.

3. **La reposición no responde a la necesidad.** Se ordena prácticamente la misma cantidad
   (~110 unidades) tanto cuando falta stock como cuando sobra. La correlación entre lo ordenado
   y la necesidad real es prácticamente nula.

4. **Ningún factor comercial mueve las ventas.** Ni el precio, ni los descuentos, ni las
   promociones/feriados, ni el clima, ni la temporada muestran un efecto medible sobre las
   ventas. Además, la demanda proyectada sigue casi perfectamente a las ventas reales
   (correlación ≈ 0,99), por lo que el problema no está en el pronóstico, sino en cómo se
   gestiona el inventario frente a esa demanda.

---

## Dataset

- **Fuente:** Retail Store Inventory Forecasting Dataset (Kaggle).
  <https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset>
- **Licencia:** CC0 1.0 — Dominio Público
  (<https://creativecommons.org/publicdomain/zero/1.0/>)
- **Volumen:** 73.100 filas × 15 columnas.
- **Período:** 2022-01-01 a 2024-01-01.
- **Grano:** cada fila representa un producto, en una tienda, en un día.
- **Naturaleza:** es un **dataset sintético** (así lo describe la propia fuente), generado para
  practicar gestión de inventario y pronóstico de demanda.

Columnas principales: `Date`, `Store ID`, `Product ID`, `Category`, `Region`,
`Inventory Level`, `Units Sold`, `Units Ordered`, `Demand Forecast`, `Price`, `Discount`,
`Weather Condition`, `Holiday/Promotion`, `Competitor Pricing`, `Seasonality`.

---

## El dashboard

La aplicación está organizada en indicadores principales (KPIs), un resumen ejecutivo dinámico
y cuatro pestañas:

- **KPIs:** ventas totales, cobertura mediana, % en riesgo de quiebre y % con inventario holgado.
- **Inventario y demanda:** evolución mensual de inventario vs demanda, zonas de cobertura,
  comparación por categoría y un tablero de diagnóstico de las situaciones más severas
  (con vista de déficit y de exceso).
- **Ventas y demanda:** ventas por categoría y comparación de ventas reales vs demanda proyectada.
- **Reposición y promociones:** análisis de si la reposición responde a la necesidad, y el
  impacto (nulo) de las promociones.
- **Datos filtrados:** tabla y descarga de los datos según los filtros.

**Filtros interactivos** (actualizan todo en tiempo real): categoría, tienda, región y rango
de fechas.

---

## Cómo ejecutar la app en local

Requiere Python 3.9 o superior.

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd sic_2026_c-p_cohort_1/proyectos/Equipo_6

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el dashboard
streamlit run app.py
```

La app carga el dataset desde `data/retail_store_inventory.csv` usando una ruta relativa al
propio `app.py`, por lo que funciona tanto en local como publicada.

---

## Dashboard publicado

> **URL pública:** `[pendiente de publicar en Streamlit Cloud]`

---

## Estructura del proyecto

```
proyectos/Equipo_6/
├── data/
│   └── retail_store_inventory.csv
├── notebooks/
│   ├── modelo.ipynb              # modelo predictivo de ventas
│   └── analisis_inventario.ipynb # análisis de inventario (cobertura, riesgo, reposición)
├── outputs/
│   └── dashboard_preview.png   # captura del dashboard
├── inventory_risk.py           # módulo de cálculo de riesgo de quiebre
├── app.py                      # dashboard Streamlit (aplicación principal)
├── requirements.txt
└── README.md
```

---

## Limitaciones (honestas)

- El dataset es **sintético**: ninguna variable comercial (precio, descuento, promoción, clima,
  temporada) explica las ventas, por lo que **no es posible hacer recomendaciones de pricing ni
  de marketing**. El análisis se concentra donde los datos sí tienen estructura: la calibración
  del inventario frente a la demanda.
- Las columnas `Region` y `Seasonality` se comportan como etiquetas casi aleatorias (no
  corresponden a una geografía ni a un calendario real), por lo que no se usan como hallazgo.
- Es una herramienta de **diagnóstico retrospectivo** sobre datos históricos, no un sistema
  operativo en tiempo real. La misma lógica, aplicada a datos actuales, sí serviría para
  monitoreo en vivo.

---

## Stack técnico

Python · Streamlit · Pandas · Plotly · NumPy · scikit-learn (modelo).

---

## Integrantes

| Rol | GitHub | Nombre |
|-----|--------|--------|
| Integrante 1 — Dataset, limpieza y EDA | [@FQut](https://github.com/FQut) | `[completar]` |
| Integrante 2 — Modelo predictivo | [@vi-llou-ta](https://github.com/vi-llou-ta) | `[completar]` |
| Integrante 3 — Dashboard | [@rariffo](https://github.com/rariffo) | Rubén Riffo García |
| Integrante 4 — Documentación y presentación | [@me1kimu](https://github.com/me1kimu) | `[completar]` |

> Nota para el equipo: completar los nombres faltantes y reemplazar la URL del dashboard una vez publicado.
