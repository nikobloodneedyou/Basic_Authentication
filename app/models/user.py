from sqlalchemy import Column, DateTime, Integer, String, func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_code = Column(String, primary_key=True, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    age = Column(Integer, nullable=False, default=18)
    role = Column(String, nullable=False, default="user")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())



