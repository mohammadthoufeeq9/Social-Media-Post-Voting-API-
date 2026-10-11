from fastapi import HTTPException,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post,User,RevokedToken,RevokedTokenFamily

from fast_app.schemas.post import(
     UserCreate,UserResponse,RefreshToken
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import create_access_token,get_current_user,create_refresh_token,SECRET_KEY,ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt,JWTError

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=201)
def reg(user_data:UserCreate,db:Session=Depends(get_db)):
     new_user=User(
          username=user_data.username,
          email=user_data.email,
          password=hash_password(user_data.password)
     )
     db.add(new_user)
     db.commit()
     db.refresh(new_user)

     return new_user

@router.post("/refresh")
def refresh_token(data:RefreshToken,db:Session=Depends(get_db)):
     try:
          playload= jwt.decode(data.refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
          if playload.get("type") != "refresh":
               raise HTTPException(status_code=401,detail="Invalid refresh token")
          jti=playload.get("jti")
          revoked=db.query(RevokedToken).filter(RevokedToken.jti==jti).first()
          if revoked is not None:
               raise HTTPException(status_code=401, detail="Refresh token has been revoked")
          user_id = playload.get('user_id')
          if user_id is None:
               raise HTTPException(status_code=401,detail="Invalid refresh_token")
          new_access_token=create_access_token({"user_id":user_id,"type":"access"})
          
     except JWTError:
          raise HTTPException(status_code=401,detail="Invalid token or token expired")
     db.add(RevokedToken(jti=jti))
     db.commit()

     new_access_token = create_access_token({
             "user_id": user_id,"type": "access"
         })
     
     new_refresh_token = create_refresh_token({"user_id": user_id})
     return {
             "access_token": new_access_token,
             "refresh_token": new_refresh_token,
             "token_type": "bearer"
         }


@router.post("/logout")
def logout(data:RefreshToken,db:Session=Depends(get_db)):
     try:
          playload=jwt.decode(data.refresh_token,SECRET_KEY,algorithms=ALGORITHM)
          if playload.get("type") != "refresh":
               raise HTTPException(status_code=401,detail="Invalid refresh token")
          jti=playload.get('jti')
          if jti is None:
               raise HTTPException(status_code=401,detail="Invalid refresh token")
          revoked = db.query(RevokedToken).filter(RevokedToken.jti== jti).first()
          if revoked is None:
            db.add(RevokedToken(jti=jti))
            db.commit()

          return {"message": "Logout successful"}
     except JWTError:
          raise HTTPException(status_code=401,detail="Invalid or expired token")

     
@router.post("/login")
def login(user_detail:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
     print("USERNAME:", user_detail.username)
     print("PASSWORD RECEIVED:", bool(user_detail.password))
     user=db.query(User).filter(User.username == user_detail.username).first()

     print("USER FOUND:", user is not None)

     if user is not None:
          if verify_hash(user_detail.password,user.password):
               access_token = create_access_token({"user_id": user.id,"type": "access"})
               refresh_token = create_refresh_token({"user_id": user.id,"type": "refresh"})
               return {
                    "Message":"Login Successfull",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "Token_type":"bearer"
               }
          raise HTTPException(status_code=401,detail="Invalid email or password")
     raise HTTPException(status_code=401,detail="Invalid email or password")