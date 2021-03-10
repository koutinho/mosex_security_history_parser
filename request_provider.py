import requests
from datetime import timedelta, datetime, date
from calendar import monthrange
from candle import Candle
import asyncio

async def get_candles_sheet_async(stock_name, candle_numbers, till):
    url = f'{PRICE_SHEET_URL}/{stock_name}.json'
    payload = {'s1.type': 'candles', 'interval': '1', 'candles': candle_numbers, 'till': till}

    r = await asyncio.to_thread(requests.get, url, params = payload)
    
    if r.status_code == 200:
        return r.json()

    return None

async def get_candles_async(stock_name, date):
    json = await get_candles_sheet_async(stock_name, 1000, date + timedelta(days=1))
    json_candles = json['zones'][0]['series'][0]['candles']
    filtered_candles = filter(lambda x: datetime.fromtimestamp(x['open_time']/1000).date() == date, json_candles)
    candles = map(lambda x: Candle(x['open'], x['close'], datetime.fromtimestamp(x['open_time']/1000), datetime.fromtimestamp(x['close_time']/1000), x['low'], x['high']), filtered_candles)
    return list(candles)

async def get_candles_for_month(stock_name, year, month):
    first_day, number_of_days = monthrange(year, month)

    days = map(lambda day_number: date(year, month, day_number), range(1, number_of_days + 1))

    requests = list(map(lambda day: get_candles_async(stock_name, day), days))

    month_candles_tasks, pending = await asyncio.wait(requests)

    candles = []
    for task in month_candles_tasks:
        if task.exception():
            continue
        for candle in task.result():
            candles.append(candle)

    return candles

PRICE_SHEET_URL = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities"