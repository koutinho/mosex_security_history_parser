import requests

def get_price_sheet(stock_name, candle_numbers, till):
    url = f'{PRICE_SHEET_URL}/{stock_name}.json'
    payload = {'s1.type': 'candles', 'interval': '1', 'candles': candle_numbers, 'till': till}
    r = requests.get(url, params = payload)
    
    if r.status_code == 200:
        return r.json()

    return None

PRICE_SHEET_URL = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities"