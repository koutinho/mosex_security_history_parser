import requests
from datetime import timedelta
from datetime import datetime
from candle import Candle

def get_price_sheet(stock_name, candle_numbers, till):
    url = f'{PRICE_SHEET_URL}/{stock_name}.json'
    payload = {'s1.type': 'candles', 'interval': '1', 'candles': candle_numbers, 'till': till}
    r = requests.get(url, params = payload)
    
    if r.status_code == 200:
        return r.json()

    return None

def get_candles(stock_name, date):
    json = get_price_sheet(stock_name, 1000, date + timedelta(days=1))
    json_candles = json['zones'][0]['series'][0]['candles']
    filtered_candles = filter(lambda x: datetime.fromtimestamp(x['open_time']/1000).date() == date, json_candles)
    candles = map(lambda x: Candle(x['open'], x['close'], datetime.fromtimestamp(x['open_time']/1000), datetime.fromtimestamp(x['close_time']/1000), x['low'], x['high']), filtered_candles)
    return list(candles)



PRICE_SHEET_URL = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities"