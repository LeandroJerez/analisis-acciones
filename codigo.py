import json

# Cargar los tickers desde el archivo externo
with open('config.json', 'r') as f:
    config = json.load(f)

tickers = config['tickers']
print(tickers)