📈 StockMetrics Studio — Financial Market Analytics Dashboard

Un panel interactivo y plataforma de análisis financiero desarrollada en Python. Combina capacidades de descarga de datos bursátiles en tiempo real mediante Yahoo Finance, dashboards web dinámicos con Streamlit e interactividad gráfica avanzada con Plotly, junto a un pipeline automatizado de procesamiento y exportación en Excel.

🌟 Características Principales

Análisis Multi-Activo Dinámico: Consulta cotizaciones, variaciones y métricas en tiempo real de acciones (EE.UU., locales), ETFs, índices y criptomonedas (ej. AAPL, MSFT, NVDA, BTC-USD, GGAL.BA).

Visualización Interactiva Avanzada:

Gráficos comparativos de rendimiento histórico ajustados y normalizados en porcentaje.

Candlestick / gráficos de líneas con herramientas de zoom, panorámica y tooltips contextuales mediante Plotly.

Métricas Clave (KPIs): Indicadores en tiempo real de precio actual, variaciones diarias e indicadores de rendimiento diario.

Pipeline de Datos Automatizado: Extracción y procesamiento automatizado para la generación de reportes estructurados con formato condicional.

Soporte para Tickers Personalizados: Búsqueda libre e incorporación dinámica de cualquier símbolo disponible en Yahoo Finance.

Exportación de Datos: Descarga de tablas consolidadas en formato CSV directamente desde la interfaz.

🛠️ Tech Stack & Arquitectura

Lenguaje Principal: Python

Interfaz Web: Streamlit

Visualización de Datos: Plotly Express

Procesamiento de Datos: Pandas

API Financiera: yfinance

Generación de Reportes: OpenPyXL

CI/CD & Automatización: GitHub Actions

📂 Estructura del Proyecto

Acciones/
│
├── .github/
│ └── workflows/
│ └── actualizar_acciones.yml # Pipeline CI/CD para automatización
│
├── stock-dashboards/
│ ├── app.py # Aplicación Web principal de Streamlit
│ └── requirements.txt # Dependencias específicas de la app web
│
├── main.py # Script principal de ejecución
├── extractor.py # Módulo de extracción vía yfinance
├── formatter.py # Módulo de formato y diseño en Excel
├── requirements.txt # Dependencias globales del proyecto
└── README.md # Documentación del proyecto

🚀 Instalación y Ejecución Local

1. Clonar el Repositorio

git clone https://github.com/LeandroJerez/analsis-acciones.git
cd analisis-acciones

2. Crear y Activar Entorno Virtual

# Windows

python -m venv .venv
.venv\Scripts\activate

# macOS / Linux

python -m venv .venv
source .venv/bin/activate

3. Instalar Dependencias

pip install -r stock-dashboards/requirements.txt

4. Ejecutar la Aplicación

cd stock-dashboards
streamlit run app.py

🌐 Despliegue en la Nube (Streamlit Cloud)

Para desplegar esta aplicación directamente en Streamlit Cloud:

Subir el proyecto a un repositorio público en GitHub.

Ir a Streamlit Community Cloud e iniciar sesión.

Crear un New App y seleccionar el repositorio.

Establecer la ruta del archivo principal (Main file path) como:

stock-dashboards/app.py

Hacer clic en Deploy.

📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más información.
