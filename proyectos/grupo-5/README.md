# 🚨 API de Alertas y Simulación de Riesgo de Incendios Forestales (Región del Biobío)

Este repositorio contiene el desarrollo del **Proyecto Final** para el curso de **Código y Programación (C&P)** de la **Cohorte 1 (2026)** de **Samsung Innovation Campus Chile**, ejecutado por **Innovacien**.

## 👥 Integrantes (Grupo 5)
* Avelyn García — *(GitHub: @AvyG)*
* Ignacio Hidalgo — *(GitHub: @IgHB27)*
* Sergio Rebolledo — *(GitHub: @sergiorebolledo)*
* Alejandro Gómez — *(GitHub: @OrPhery1)*
* Pablo Mellado — *(GitHub: NoBugPablito)*
* [Nombre Integrante 6] — *(GitHub: @usuario6)*

---

## 📝 1. Descripción del Proyecto y Contexto
Los incendios forestales constituyen una amenaza socioambiental permanente y crítica en Chile. Durante las últimas temporadas estivales, cientos de siniestros han afectado miles de hectáreas y damnificado a comunidades enteras, concentrándose históricamente un alto índice de severidad en la **Región del Biobío** debido a su matriz productiva.

Este proyecto implementa un **Simulador Técnico Integrado de Gestión de Emergencias y Evacuación Territorial**. Su objetivo es actuar como un Producto Mínimo Viable (MVP) analítico que representa de forma lógica cómo la interacción de variables atmosféricas dinámicas y la matriz de combustible vegetal expanden o contraen el riesgo de propagación del fuego entre localidades civiles, buscando concientizar y preparar a la población ante escenarios críticos de riesgo.

### 📊 Datos Utilizados
El sistema se nutre de inventarios territoriales fijos de la Región del Biobío y un set de datos geográficos depurado (`biobio_limpio.csv`):
* **Plantación Forestal:** 875.178,4 ha (Ponderación de combustible más alta por su continuidad vertical y horizontal).
* **Bosque Nativo:** 597.572,7 ha
* **Bosque Mixto:** 51.635,9 ha
* **Humedales:** 10.172,8 ha
* **Superficie Total Regional:** 2.399.067,7 ha

---

## ❓ 2. Pregunta de Análisis (Valor del Análisis)
> ¿De qué manera las fluctuaciones simultáneas de factores climatológicos críticos interactúan con la composición forestal del Biobío para determinar el radio de alcance kilométrico de un incendio y cuánta infraestructura habitacional civil se expone directamente a vectores de peligro en una ventana temporal dada?

---

## 🧮 3. Fundamentación Científica y Arquitectura Lógica

### 🧪 Relación Química: El Tetraedro del Fuego en los Controles Dinámicos
Mientras el modelo de Rothermel rige la física espacial del avance, los controles deslizantes (*sliders*) de la interfaz emulan la química básica del **Tetraedro del Fuego** (Combustible, Oxígeno, Calor y Reacción en Cadena):
* **Combustible:** Modulado internamente por la densidad y continuidad de las *Plantaciones Forestales*.
* **Calor:** Influenciado por el control de *Temperatura Ambiente*, acelerando la energía de ignición.
* **Oxígeno:** Alimentado cinéticamente por la *Velocidad del Viento*, el cual actúa como el comburente que aviva la llama.
* **Reacción en Cadena:** Determinada inversamente por la *Humedad Relativa*. Los escenarios de alta *Sequedad* eliminan la barrera térmica del agua, permitiendo la transferencia autosostenible de calor entre partículas vegetales.

### 🔬 Inspiración: El Modelo Matemático de Rothermel (1972)
El diseño lógico de este simulador se basa conceptualmente en las variables del **Modelo de Propagación de Richard Rothermel ($1972$)**, la ecuación física estándar utilizada por agencias internacionales para calcular la velocidad del frente de fuego ($R$):

$$R = \frac{I_R \times \xi \times (1 + \Phi_w + \Phi_s)}{\rho_b \times \varepsilon \times Q_{ig}}$$

* **El Desafío Técnico (Contras):** Implementar la ecuación de Rothermel de forma exacta en un software de tiempo real requiere parámetros de laboratorio de alta especificidad difíciles de obtener dinámicamente en un curso inicial (como la carga molecular del combustible, tamaño microscópico de partículas, humedad interna del combustible fino muerto, densidad de empaquetamiento y energía neta de ignición $Q_{ig}$).
* **La Solución del Equipo (Pros):** Para construir una aplicación ágil, interactiva y de alto valor educativo, simplificamos los factores físicos del modelo de Rothermel (combustible, viento $\Phi_w$, pendiente $\Phi_s$ y temperatura ambiental) y los estructuramos en un sistema matricial lineal de pesos ponderados.

### 🧮 Ecuaciones del Algoritmo del Grupo 5

#### A. Factor Combustible
$$\text{Combustible} = \frac{(\text{Plantación Forestal} \times 1.0) + (\text{Bosque Mixto} \times 0.8) + (\text{Bosque Nativo} \times 0.6)}{\text{Bosques Total}} \times 100$$

#### B. Índice General de Propagación (IP)
$$\text{IP} = (0.30 \times \text{Viento}) + (0.30 \times \text{Combustible}) + (0.20 \times \text{Temperatura}) + (0.10 \times \text{Sequedad}) + (0.10 \times \text{Pendiente})$$
*Donde: $\text{Sequedad} = 100 - \text{Humedad Relativa}$*

#### C. Velocidad y Alcance Expansivo
$$\text{Velocidad (km/h)} = 0.5 + \left(\frac{\text{IP}}{100} \times 4.0\right) + \left(\frac{\text{Viento}}{100} \times 3.0\right)$$
$$\text{Alcance (Km)} = \text{Velocidad} \times \text{Tiempo}$$

#### D. Probabilidad de Afectación por Comuna
$$\text{Probabilidad (\%)} = 100 - \left(\frac{\text{Distancia}}{\text{Alcance}} \times 100\right)$$

---

## 🚦 4. Estandarización de Alertas y Criterios Técnicos (Chile)

El sistema integra y traduce las reglas operativas reales de la institucionalidad chilena para clasificar el nivel de riesgo en la interfaz cartográfica:

### 🔴 Lógica del "Botón Rojo" (CONAF)
La aplicación emula la condición de alerta extrema de la Corporación Nacional Forestal. El sistema estresa los indicadores del mapa de calor y dispersión basándose en la superposición de condiciones críticas simultáneas:
* **Probabilidad de Ignición:** $\ge 70\%$ (representada en el simulador mediante humedades relativas inferiores al $20\%$ y altas temperaturas).
* **Velocidad del Viento:** $\ge 20\text{ km/h}$ mínimos para activar la propagación cinética descontrolada.

### 🗺️ Clasificación de Rangos de Probabilidad e Institucionalidad (SENAPRED)
Una vez calculada la distancia geodésica respecto al foco, el mapa de dispersión (`scatter_mapbox`) clasifica las localidades en cuatro umbrales con los colores técnicos oficiales de emergencia:

* **75 a 100% | 🔴 Extremo (Alerta Roja):** Amenaza inminente a vidas humanas, viviendas e infraestructura crítica. Requiere la simulación de evacuación obligatoria.
* **50 a 74% | 🟠 Alto (Alerta Amarilla):** El siniestro presenta proyecciones de crecimiento que amenazan con superar las capacidades locales de control.
* **25 a 49% | 🟡 Medio (Alerta Temprana Preventiva):** Estado de anticipación coordinado por variables meteorológicas extremas (viento adverso y calor).
* **0 a 24% | 🟢 Bajo (Alerta Verde / Territorio Seguro):** Condiciones bajo control técnico o fuera del cono de trayectoria del vector de viento.

---

## 📂 5. Estructura Obligatoria del Repositorio
```text
proyectos/grupo5-api-incendios/
├── data/
│   ├── Latitud - Longitud Chile.csv   # Coordenadas base originales del territorio nacional
│   └── biobio_limpio.csv               # Dataset depurado y filtrado para la región
├── notebooks/
│   └── 01_geografia_y_poblacion.ipynb # Jupyter Notebook con el EDA y procesamiento de datos
├── outputs/
│   └── dashboard_preview.png          # Captura de pantalla de la interfaz interactiva corriendo
├── app.py                             # Código fuente de la aplicación en Streamlit
├── requirements.txt                   # Librerías necesarias para el despliegue del servidor
└── README.md                          # Documentación del proyecto (Este archivo)
