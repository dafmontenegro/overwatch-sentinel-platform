from .database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"  # Nombre exacto de la tabla

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    provider_id = Column(String, unique=True)
    email = Column(String, unique=True)