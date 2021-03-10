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

    session = Session()

    stock = add_stock_to_db_if_not_exists(session, code, description)

    from_total_month = from_year * 12 + from_month
    to_total_month = to_year * 12 + to_month

    months_to_parse = [(month // 12, month % 12) for month in range(from_total_month, to_total_month + 1)]

    for month in months_to_parse:
        logging.info(f'Удаление свечей для {month[0]}.{month[1]}')
        delete_stocks(session, month[0], month[1])

        logging.info(f'Получение свечей для {month[0]}.{month[1]}')
        candles = await get_candles_for_month(code, month[0], month[1])
        
        db_candles = map(lambda x: Candle(x.open_price, x.close_price, x.open_time, x.close_time, x.low, x.high), candles)
        stock.candles.extend(db_candles)

        logging.info(f'Сохранение свечей акций {description} для месяца {month[0]}.{month[1]} в БД')
        session.commit()

    session.close()

def add_stock_to_db_if_not_exists(session, code, description):
    stock = session.query(Stock).filter(Stock.code == code).first()

    if not stock:
        stock = Stock(code, description)
        session.add(stock)
        session.commit()

    return stock   

def delete_stocks(session, year, month):
    session.query(Candle).filter(extract('year', Candle.open_time) == year).\
        filter(extract('month', Candle.open_time) == month).\
            delete(synchronize_session="fetch")

    session.commit()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))