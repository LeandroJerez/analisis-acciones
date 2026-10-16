import json
import yfinance as yf
import pandas as pd


def obtener_datos_acciones():
    # Cargar tickers desde config.json
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    tickers = config['tickers']

    datos_acciones = []
    print("Descargando datos del mercado...")

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")

            if not hist.empty:
                precio_actual = hist['Close'].iloc[-1]
                cierre_anterior = info.get(
                    'previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else precio_actual)

                variacion_diaria_val = precio_actual - cierre_anterior
                variacion_diaria_porc = (
                    variacion_diaria_val / cierre_anterior) * 100

                datos_acciones.append({
                    "Ticker": ticker,
                    "Nombre": info.get('shortName', ticker),
                    "Precio Actual": round(precio_actual, 2),
                    "Cierre Anterior": round(cierre_anterior, 2),
                    "Var. Diaria ($)": round(variacion_diaria_val, 2),
                    "Var. Diaria (%)": round(variacion_diaria_porc, 2)
                })
        except Exception as e:
            print(f"No se pudieron obtener datos para {ticker}: {e}")

    return pd.DataFrame(datos_acciones)
