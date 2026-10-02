from sqlalchemy import Boolean,Integer,Text, func
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
# from pydantic import BaseModel,ConfigDict

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__="posts"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(Text)
    content:Mapped[str]=mapped_column(Text)
    published:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(server_default=func.now())
