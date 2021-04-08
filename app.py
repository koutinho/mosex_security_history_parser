from data_layer.session import Session
from data_layer.stock import Stock
from data_layer.candle import Candle
from datetime import datetime, date, timedelta
from request_provider import get_candles_for_month
from sqlalchemy import extract  
import sys, getopt
import logging
import asyncio

async def main(argv):
    opts, _ = getopt.getopt(argv, '', ['code=','description=','from_year=', 'from_month=','to_year=','to_month=', 'log='])

    for opt, arg in opts:
        if opt == '--code':
            code = arg
        elif opt == '--description':
            description = arg
        elif opt == '--from_year':
            from_year = int(arg)
        elif opt == '--from_month':
            from_month = int(arg)
        elif opt == '--to_year':
            to_year = int(arg)
        elif opt == '--to_month':
            to_month = int(arg)
        elif opt == '--log':
            loglevel = getattr(logging, arg.upper())
            logging.basicConfig(level=loglevel)

    stock = add_stock_to_db_if_not_exists(code, description)

    from_total_month = from_year * 12 + from_month
    to_total_month = to_year * 12 + to_month

    months_to_parse = [((month - 1) // 12, ((month - 1) % 12) + 1) for month in range(from_total_month, to_total_month + 1)]

    for month in months_to_parse:
        logging.info(f'Удаление свечей для {month[0]}.{month[1]}')
        delete_stocks(month[0], month[1])

        logging.info(f'Получение свечей для {month[0]}.{month[1]}')
        candles = await get_candles_for_month(code, month[0], month[1])

        logging.info(f'Сохранение свечей акций {description} для месяца {month[0]}.{month[1]} в БД')
        add_candles_to_stock(stock, candles)

def add_stock_to_db_if_not_exists(code, description):
    session = Session(expire_on_commit=False)

    stock = session.query(Stock).filter(Stock.code == code).first()

    if not stock:
        stock = Stock(code, description)
        session.add(stock)
        session.commit()

    session.close()

    return stock   

def delete_stocks(year, month):
    session = Session()

    session.query(Candle).filter(extract('year', Candle.open_time) == year).\
        filter(extract('month', Candle.open_time) == month).\
            delete(synchronize_session=False)

    session.commit()

    session.close()

def add_candles_to_stock(stock, candles):
    session = Session()

    db_candles = map(lambda x: dict(open_price = x.open_price, close_price = x.close_price, open_time = x.open_time, close_time = x.close_time, low = x.low, high = x.high, stock_id = stock.id), candles)
    session.bulk_insert_mappings(Candle, db_candles)

    session.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))