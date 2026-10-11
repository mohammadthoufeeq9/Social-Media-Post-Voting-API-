from dotenv import load_dotenv
from jose import jwt,JWTError
from datetime import datetime,timezone,timedelta
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from fast_app.database.database import get_auth_db
from fast_app.models.post import User
from fastapi import Depends,HTTPException
from uuid import uuid4

load_dotenv("D:\\FASTAPI\\api_app\\.env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(days=7)
    to_encode.update({"exp":expire,"type":"refresh","jti":str(uuid4())})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

oauth_scheme=OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(token:str=Depends(oauth_scheme),db=Depends(get_auth_db)):
    try:
        play_load=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=play_load.get("user_id")
        if play_load.get('type') != 'acccess':
            raise HTTPException(status_code=401, detail='Invalid access token')
        if user_id is None:
            raise HTTPException(status_code=401 ,detail="User not found")
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user=db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401,detail="user not found")
    return user

def test_user():
    return{
        "username":"Thoufeeq",
        "id":5
    }
        
    