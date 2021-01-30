from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from data_layer.base import Base
from sqlalchemy.orm import relationship

class Candle(Base):
    __tablename__ = 'candles'

    id = Column(Integer, primary_key = True)
    open_price = Column(Float)
    close_price = Column(Float)
    open_time = Column(DateTime)
    close_time = Column(DateTime)
    low = Column(Float)
    high = Column(Float)

    stock_id = Column(Integer, ForeignKey('stocks.id'))
    stock = relationship("Stock", back_populates="candles")