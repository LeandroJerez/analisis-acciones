import yfinance as yf
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import logging

# ============================================================
# STOCK DASHBOARD
# Panel interactivo de análisis financiero de acciones
# Tecnologías: Streamlit, yfinance, Pandas y Plotly Express
# ============================================================


# ------------------------------------------------------------
# 1. CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# ------------------------------------------------------------

st.set_page_config(
    page_title="Stock Dashboard | Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

PERIOD_OPTIONS = {
    "1 mes": "1mo",
    "3 meses": "3mo",
    "6 meses": "6mo",
    "1 año": "1y",
    "2 años": "2y",
    "5 años": "5y",
}

# Estilos personalizados para conseguir una interfaz profesional.
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1 {
            letter-spacing: -1px;
        }

        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.07);
            border: 1px solid rgba(128, 128, 128, 0.18);
            padding: 18px;
            border-radius: 12px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.15);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 2. FUNCIONES PARA DESCARGAR Y PROCESAR LOS DATOS
# ------------------------------------------------------------

@st.cache_data(ttl=900, show_spinner=False)
def download_stock_data(tickers: tuple, period: str) -> pd.DataFrame:
    """
    Descarga precios históricos ajustados de Yahoo Finance.

    Args:
        tickers: Tupla de símbolos bursátiles.
        period: Período histórico compatible con yfinance.

    Returns:
        DataFrame con una columna por ticker y el índice de fechas.
    """
    tickers = tuple(dict.fromkeys(
        ticker.strip().upper()
        for ticker in tickers
        if ticker and ticker.strip()
    ))

    if not tickers:
        return pd.DataFrame()

    try:
        raw_data = yf.download(
            tickers=list(tickers),
            period=period,
            interval="1d",
            auto_adjust=True,
            group_by="ticker",
            progress=False,
            threads=True,
            timeout=20,
        )

        if raw_data is None or raw_data.empty:
            return pd.DataFrame()

        close_data = pd.DataFrame(index=raw_data.index)

        # Yahoo Finance puede devolver columnas simples o MultiIndex.
        for ticker in tickers:
            try:
                if isinstance(raw_data.columns, pd.MultiIndex):
                    ticker_data = None

                    # Formato habitual: (ticker, campo).
                    if ticker in raw_data.columns.get_level_values(0):
                        ticker_data = raw_data[ticker]

                    # Compatibilidad con el formato (campo, ticker).
                    elif ticker in raw_data.columns.get_level_values(1):
                        ticker_data = raw_data.xs(
                            ticker, axis=1, level=1
                        )

                    if ticker_data is not None and "Close" in ticker_data:
                        close_data[ticker] = ticker_data["Close"]

                elif "Close" in raw_data.columns:
                    # Respuesta de un solo ticker.
                    close_data[ticker] = raw_data["Close"]

            except (KeyError, TypeError, ValueError) as exc:
                logger.warning(
                    "No se pudo extraer el precio de %s: %s",
                    ticker,
                    exc,
                )

        close_data.index = pd.to_datetime(close_data.index)
        close_data = close_data.sort_index()
        close_data = close_data[~close_data.index.duplicated(keep="last")]
        close_data = close_data.apply(pd.to_numeric, errors="coerce")
        close_data = close_data.dropna(how="all")

        # Eliminar columnas sin datos válidos.
        close_data = close_data.dropna(axis=1, how="all")

        return close_data

    except Exception as exc:
        logger.exception("Error descargando datos bursátiles: %s", exc)
        return pd.DataFrame()


# ------------------------------------------------------------
# 3. FUNCIONES AUXILIARES
# ------------------------------------------------------------

def format_price(value: float) -> str:
    """Formatea un precio en dólares estadounidenses."""
    if pd.isna(value):
        return "N/D"

    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Formatea una variación porcentual."""
    if pd.isna(value):
        return "N/D"

    return f"{value:+.2f}%"


def calculate_daily_change(series: pd.Series):
    """
    Calcula la variación entre los dos últimos cierres disponibles.
    Devuelve el último precio y la variación porcentual diaria.
    """
    valid_prices = series.dropna()

    if valid_prices.empty:
        return None, None

    latest_price = float(valid_prices.iloc[-1])

    if len(valid_prices) < 2:
        return latest_price, None

    previous_price = float(valid_prices.iloc[-2])

    if previous_price == 0:
        return latest_price, None

    daily_change = (
        (latest_price - previous_price) / previous_price
    ) * 100

    return latest_price, daily_change


def build_long_dataframe(price_data: pd.DataFrame) -> pd.DataFrame:
    """Convierte la matriz de precios a formato largo para Plotly."""
    long_data = (
        price_data.rename_axis("Fecha")
        .reset_index()
        .melt(
            id_vars="Fecha",
            var_name="Ticker",
            value_name="Precio",
        )
        .dropna(subset=["Precio"])
    )

    return long_data


# ------------------------------------------------------------
# 4. ENCABEZADO PRINCIPAL
# ------------------------------------------------------------

st.title("📈 StockMetrics Studio")
st.caption(
    "MARKET ANALYTICS  /  EQUITY MONITORING  /  HISTORICAL PERFORMANCE"
)

st.markdown(
    """
    Panel interactivo para analizar precios históricos, comparar
    acciones y monitorear variaciones del mercado. Los datos se
    obtienen de Yahoo Finance y pueden presentar retrasos o
    interrupciones.
    """
)

st.divider()


# ------------------------------------------------------------
# 5. BARRA LATERAL: CONTROLES
# ------------------------------------------------------------

with st.sidebar:
    st.header("🔎 Búsqueda")

    st.markdown("### Activos financieros")

    ticker_input = st.multiselect(
        "Seleccioná las acciones",
        options=sorted(set(DEFAULT_TICKERS)),
        default=["AAPL", "MSFT", "NVDA"],
        help=(
            "Elegí uno o varios activos. También podés escribir "
            "un símbolo bursátil personalizado."
        ),
        accept_new_options=True,
        placeholder="Ej.: AAPL, MSFT, TSLA",
    )

    tickers = list(
        dict.fromkeys(
            ticker.strip().upper()
            for ticker in ticker_input
            if ticker and ticker.strip()
        )
    )

    st.markdown("### Período histórico")

    selected_period_label = st.selectbox(
        "Rango temporal",
        options=list(PERIOD_OPTIONS.keys()),
        index=3,
    )

    selected_period = PERIOD_OPTIONS[selected_period_label]

    st.markdown("### Visualización")

    normalize_prices = st.toggle(
        "Comparar rendimiento porcentual",
        value=False,
        help=(
            "Compara la evolución desde el inicio del período. "
            "Es útil cuando las acciones tienen precios diferentes."
        ),
    )

    show_table = st.toggle(
        "Mostrar tabla histórica",
        value=True,
    )

    st.divider()

    if st.button("🔄 Actualizar datos", use_container_width=True):
        download_stock_data.clear()
        st.rerun()

    st.caption("Fuente de datos: Yahoo Finance")
    st.caption("Caché de datos: 15 minutos")


# ------------------------------------------------------------
# 6. VALIDACIÓN Y DESCARGA
# ------------------------------------------------------------

if not tickers:
    st.info(
        "Seleccioná al menos un ticker en la barra lateral "
        "para comenzar el análisis."
    )
    st.stop()

with st.spinner("Descargando datos del mercado..."):
    prices = download_stock_data(tuple(tickers), selected_period)

if prices.empty:
    st.error(
        "No se pudieron obtener datos históricos. Verificá los "
        "tickers o tu conexión a Internet e intentá nuevamente."
    )
    st.stop()

available_tickers = list(prices.columns)
missing_tickers = sorted(set(tickers) - set(available_tickers))

if missing_tickers:
    st.warning(
        "No se encontraron datos para: "
        + ", ".join(missing_tickers)
    )

if not available_tickers:
    st.error("No hay activos con datos válidos para analizar.")
    st.stop()

latest_date = prices.dropna(how="all").index.max()

if pd.notna(latest_date):
    st.caption(
        f"Última fecha disponible: {latest_date.strftime('%d/%m/%Y')} "
        f"· Activos disponibles: {len(available_tickers)}"
    )


# ------------------------------------------------------------
# 7. TARJETAS KPI: PRECIO Y VARIACIÓN DIARIA
# ------------------------------------------------------------

st.subheader("Resumen del mercado")

metric_columns = st.columns(len(available_tickers))

for column, ticker in zip(metric_columns, available_tickers):
    latest_price, daily_change = calculate_daily_change(prices[ticker])

    with column:
        st.metric(
            label=f"{ticker} · Último cierre",
            value=format_price(latest_price),
            delta=format_percentage(daily_change),
            delta_color="normal",
            help=(
                "El precio corresponde al último cierre disponible. "
                "La variación se calcula respecto al cierre anterior "
                "disponible, no necesariamente al día calendario anterior."
            ),
        )

st.divider()


# ------------------------------------------------------------
# 8. GRÁFICO INTERACTIVO CON PLOTLY EXPRESS
# ------------------------------------------------------------

st.subheader("Evolución de las acciones")

long_data = build_long_dataframe(prices)

if normalize_prices:
    # Base 100 para comparar rendimientos desde el primer precio válido.
    normalized_data = prices.copy()

    for ticker in normalized_data.columns:
        valid_prices = normalized_data[ticker].dropna()

        if not valid_prices.empty:
            initial_price = valid_prices.iloc[0]

            if initial_price != 0:
                normalized_data[ticker] = (
                    normalized_data[ticker] / initial_price - 1
                ) * 100

    chart_data = build_long_dataframe(normalized_data)
    chart_data["Precio"] = chart_data["Precio"].round(2)

    y_axis_title = "Rendimiento desde el inicio (%)"
    chart_title = "Rendimiento porcentual comparado"
    hover_template = (
        "<b>%{fullData.name}</b><br>"
        "Fecha: %{x|%d/%m/%Y}<br>"
        "Rendimiento: %{y:.2f}%"
        "<extra></extra>"
    )

else:
    chart_data = long_data
    y_axis_title = "Precio de cierre ajustado (USD)"
    chart_title = "Evolución histórica de precios"
    hover_template = (
        "<b>%{fullData.name}</b><br>"
        "Fecha: %{x|%d/%m/%Y}<br>"
        "Precio: $%{y:,.2f}"
        "<extra></extra>"
    )

fig = px.line(
    chart_data,
    x="Fecha",
    y="Precio",
    color="Ticker",
    title=chart_title,
    template="plotly_dark",
    labels={
        "Fecha": "Fecha",
        "Precio": y_axis_title,
        "Ticker": "Activo",
    },
    hover_data={"Fecha": "|%d/%m/%Y"},
)

fig.update_traces(
    line=dict(width=2.5),
    hovertemplate=hover_template,
)

fig.update_layout(
    height=520,
    margin=dict(l=15, r=15, t=65, b=15),
    hovermode="x unified",
    legend_title_text="Ticker",
    xaxis=dict(
        title="Fecha",
        showgrid=False,
        rangeslider=dict(visible=False),
    ),
    yaxis=dict(
        title=y_axis_title,
        showgrid=True,
        zeroline=False,
    ),
)

fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1A", step="year", stepmode="backward"),
            dict(step="all", label="Todo"),
        ]
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displaylogo": False,
        "scrollZoom": True,
        "responsive": True,
    },
)

if normalize_prices:
    st.caption(
        "Un valor de +10% indica una suba del 10% respecto del "
        "primer precio válido del período seleccionado."
    )


# ------------------------------------------------------------
# 9. TABLA HISTÓRICA Y DESCARGA CSV
# ------------------------------------------------------------

if show_table:
    st.divider()
    st.subheader("Historial de precios")

    # Orden cronológico descendente: primero la fecha más reciente.
    recent_prices = prices.sort_index(ascending=False).copy()

    recent_prices.index.name = "Fecha"

    # Mostrar los últimos 30 registros sin limitar el CSV exportado.
    st.dataframe(
        recent_prices.head(30).style.format("{:,.2f}", na_rep="N/D"),
        use_container_width=True,
        height=450,
    )

    st.caption(
        "La tabla muestra los últimos 30 registros. "
        "El archivo CSV incluye todo el historial descargado."
    )

else:
    st.info(
        "La tabla histórica está oculta. Activala desde la barra lateral "
        "si querés consultar los precios."
    )


# ------------------------------------------------------------
# 10. EXPORTACIÓN DE DATOS
# ------------------------------------------------------------

st.subheader("Exportar análisis")

csv_data = prices.copy()
csv_data.index.name = "Fecha"

csv_bytes = csv_data.to_csv(
    date_format="%Y-%m-%d",
    float_format="%.6f",
    na_rep="",
).encode("utf-8-sig")

file_timestamp = datetime.now().strftime("%Y%m%d_%H%M")

st.download_button(
    label="⬇️ Descargar datos en CSV",
    data=csv_bytes,
    file_name=f"stock_dashboard_{file_timestamp}.csv",
    mime="text/csv",
    use_container_width=False,
    help=(
        "Descarga la matriz completa de precios históricos "
        "de los activos disponibles."
    ),
)


# ------------------------------------------------------------
# 11. PIE DE PÁGINA
# ------------------------------------------------------------

st.divider()

st.caption(
    "Stock Dashboard · Python + Streamlit + Plotly · "
    "Datos proporcionados por Yahoo Finance."
)

st.caption(
    "Este panel tiene fines informativos y educativos. "
    "No constituye asesoramiento financiero ni una recomendación "
    "de compra o venta de activos."
)
