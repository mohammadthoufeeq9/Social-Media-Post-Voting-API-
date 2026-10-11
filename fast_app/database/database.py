from sqlalchemy import engine,text,create_engine
from sqlalchemy.orm import sessionmaker
from fast_app.models.post import Base
import os
from dotenv import load_dotenv
load_dotenv("D:\\FASTAPI\\api_app\\.env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

Sessionlocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)