# PSet #4: Optimización de Gastos de Marketing para Showz

## Descripción General

Este proyecto analiza los datos de marketing digital de Showz, una empresa de venta de entradas para eventos, correspondientes al período de junio de 2017 a mayo de 2018. El objetivo es comprender el comportamiento de los clientes, evaluar la efectividad de las diferentes fuentes de adquisición y optimizar la inversión en marketing.

## Objetivos del Proyecto

- Analizar el comportamiento de los clientes (visitas, sesiones, frecuencia de retorno).
- Determinar el momento en que los usuarios comienzan a comprar (tiempo hasta la conversión).
- Calcular los ingresos generados por cada cliente a lo largo del tiempo (Lifetime Value - LTV) por cohortes.
- Evaluar la rentabilidad de la inversión en marketing (Costo de Adquisición de Clientes - CAC y Retorno de la Inversión en Marketing - ROMI) por fuente.
- Proponer una estrategia de asignación presupuestaria optimizada basada en datos.

## Fuentes de Datos

Los análisis se basan en tres conjuntos de datos principales:

-   `costs_us.csv`: Contiene los gastos de marketing diarios desglosados por fuente (`source_id`, `dt`, `costs`).
-   `orders_log_us.csv`: Registra las órdenes de compra realizadas por los usuarios (`Uid`, `Buy_Ts`, `Revenue`).
-   `visits_log_us.csv`: Almacena información sobre las sesiones de los usuarios en el sitio web (`Uid`, `Device`, `Start_Ts`, `End_Ts`, `Source_Id`).

## Estructura del Repositorio

```
.
├── data/
│   ├── raw/        # Archivos CSV originales (costs_us.csv, orders_log_us.csv, visits_log_us.csv)
│   ├── interim/    # Datos limpios y preprocesados (costs.csv, ordenes.csv, visitas.csv)
│   └── processed/  # Tablas agregadas generadas durante el análisis (cohortes_conversion.csv, ltv.csv, cac_por_fuente.csv, romi_por_fuente.csv)
├── notebooks/
│   └── PSet4_Showz_Marketing.ipynb  # Notebook principal con todo el análisis, visualizaciones y conclusiones
├── src/
│   ├── data_prep.py  # Módulo con funciones para carga, limpieza y preparación de datos (Clase Eda)
│   └── metrics.py    # Módulo con funciones para calcular métricas clave (cohortes, LTV, CAC, ROMI)
├── reports/
│   ├── figures/      # Gráficos generados por el análisis (DAU_WAU_MAU.png, sesiones_x_dia.png, etc.)
│   └── executive_summary.md # Resumen ejecutivo de los hallazgos y recomendaciones
├── requirements.txt  # Dependencias del proyecto
├── .gitignore        # Archivos a ignorar por Git
└── README.md         # Este archivo
```

## Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/Pablouski7/pset4.git
    cd pset4
    ```

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    ```

3.  **Activar el entorno virtual:**
    *   Windows: `.\venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

4.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Cómo Ejecutar el Análisis

1.  Asegúrate de que los archivos de datos brutos (`costs_us.csv`, `orders_log_us.csv`, `visits_log_us.csv`) estén ubicados en la carpeta `data/raw/`.
2.  Abre y ejecuta el Jupyter Notebook `notebooks/PSet4_Showz_Marketing.ipynb`.
3.  Ejecuta las celdas del notebook en orden secuencial. El notebook cargará los datos, realizará la limpieza y preprocesamiento (guardando versiones intermedias en `data/interim/`), calculará las métricas, generará visualizaciones (guardadas en `reports/figures/`), y guardará los resultados procesados (en `data/processed/`).

## Resumen del Análisis y Hallazgos Clave

El notebook `PSet4_Showz_Marketing.ipynb` contiene el análisis detallado, que incluye:

1.  **Preparación de Datos:** Carga, limpieza, transformación de tipos de datos y estandarización de nombres de columnas.
2.  **Análisis de Visitas:**
    *   Cálculo y visualización de DAU, WAU, MAU.
    *   Análisis de sesiones diarias y duración promedio de sesión.
    *   Estudio de la frecuencia de retorno de los usuarios.
3.  **Análisis de Ventas:**
    *   Determinación del tiempo hasta la primera compra (conversión).
    *   Análisis de pedidos mensuales y ticket promedio.
    *   Cálculo del LTV por cohortes mensuales de adquisición.
4.  **Análisis de Marketing:**
    *   Evaluación de los costos totales y por fuente.
    *   Cálculo del CAC por fuente.
    *   Cálculo del ROMI por fuente.
5.  **Conclusiones y Recomendaciones:**
    *   Identificación de las fuentes de marketing más y menos rentables (Fuente 1 y 2 muy rentables, Fuente 3 ineficiente).
    *   Propuesta de redistribución del presupuesto de marketing para maximizar el ROMI.
    *   Discusión de supuestos y limitaciones del análisis.

*(Un resumen más detallado se encuentra en `reports/executive_summary.md`)*
