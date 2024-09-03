from sqlalchemy import Boolean, Column, Integer, String
from url_shortener.utils.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)  # Auto generated internally
    email = Column(String, unique=True, index=True)
    fullname = Column(String)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String)
