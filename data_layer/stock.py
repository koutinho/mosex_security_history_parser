from sqlalchemy import Column, Integer, String
from data_layer.base import Base
from sqlalchemy.orm import relationship

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key = True)
    code = Column(String)
    name = Column(String)

    candles = relationship("Candle", back_populates="stock")