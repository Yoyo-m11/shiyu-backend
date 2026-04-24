from sqlalchemy import Column, Integer, String, Text, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)         # lost / found
    category = Column(String, nullable=False)     # 数码 / 证件 / 书籍...
    time = Column(String, nullable=False)         # 先用字符串，开发最快
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    images = Column(Text, nullable=False)         # 用字符串存 JSON
    contact = Column(String, nullable=False)
    status = Column(String, default="pending")
    similarity = Column(Float, default=0.0)
    match_reason = Column(Text, default="[]")     # 用字符串存 JSON
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)