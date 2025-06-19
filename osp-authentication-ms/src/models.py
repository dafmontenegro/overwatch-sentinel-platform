from .database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)
    provider_id = Column(String, index=True, unique=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)