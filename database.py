from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    image_url = Column(String(200))
    download_link = Column(String(200), nullable=False)
    currency = Column(String(10), default=Config.DEFAULT_CURRENCY)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String(50), primary_key=True)  # Plisio invoice ID
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # pending/completed/expired
    created_at = Column(Float)  # timestamp

# 初始化数据库
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
