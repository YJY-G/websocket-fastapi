from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    user_type = Column(String,default="user")


class ChatMessage(Base):  
    __tablename__ = "chat_messages"  
    id = Column(Integer, primary_key=True)  
    content = Column(String(500))  
    sender_id = Column(Integer, ForeignKey("users.id"))  
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))  
    