from sqlalchemy import Boolean,Integer,Text, func,ForeignKey,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__="posts"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(Text)
    content:Mapped[str]=mapped_column(Text)
    published:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(server_default=func.now())
    author_id:Mapped[int]=mapped_column(Integer,ForeignKey("Users.id"))

class User(Base):
    __tablename__="Users"
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(Text,unique=True)
    email:Mapped[str]=mapped_column(Text,unique=True)
    password:Mapped[str]=mapped_column(Text)
    is_admin:Mapped[bool]=mapped_column(default=False)
    Bio:Mapped[str]=mapped_column(Text,nullable=True)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(255), primary_key=True)
    revoked_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Vote(Base):
    __tablename__="votes"
    post_id:Mapped[int]=mapped_column(Integer,ForeignKey("posts.id",ondelete='CASCADE'),primary_key=True)
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey('Users.id',ondelete='CASCADE'),primary_key=True)

class RevokedTokenFamily(Base):
    __tablename__ = "revoked_token_families"

    family_id: Mapped[str] = mapped_column(String(36),primary_key=True)
    revoked_at: Mapped[datetime] = mapped_column(server_default=func.now())