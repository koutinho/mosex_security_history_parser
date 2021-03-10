from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from data_layer.base import Base
from sqlalchemy.orm import relationship

class Candle(Base):
    __tablename__ = 'candles'

    def __init__(self, open_price, close_price, open_time, close_time, low, high):
        self.open_price = open_price
        self.close_price = close_price
        self.open_time = open_time
        self.close_time = close_time
        self.low = low
        self.high = high

    id = Column(Integer, primary_key = True)
    open_price = Column(Float, index = True)
    close_price = Column(Float, index = True)
    open_time = Column(DateTime, index = True)
    close_time = Column(DateTime, index = True)
    low = Column(Float)
    high = Column(Float)

    stock_id = Column(Integer, ForeignKey('stocks.id'))
    stock = relationship("Stock", back_populates="candles")