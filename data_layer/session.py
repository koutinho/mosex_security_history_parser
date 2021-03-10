from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_layer.base import Base
from data_layer.candle import Candle
from data_layer.stock import Stock

engine = create_engine('sqlite:///mosex.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)