from fastapi import HTTPException,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import status

from fast_app.database.database import get_db
from fast_app.models.post import User,RevokedToken,RevokedTokenFamily,RevokedToken

from fast_app.schemas.post import(
     UserCreate,UserResponse,RefreshToken
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import create_access_token,create_refresh_token,SECRET_KEY,ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt,JWTError
from uuid import uuid4

from fast_app.utils.rate_limit import limiter
from fastapi import Request

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=201)
@limiter.limit('1/minute')
def reg(request:Request,user_data:UserCreate,db:Session=Depends(get_db)):
     existing_user=db.query(User).filter(User.email == user_data.email).first()
     if existing_user is not None:
          raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='A user with this email already exists')
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
@limiter.limit('10/minute')
def refresh_token(request:Request,data:RefreshToken,db:Session=Depends(get_db)):
     try:
          playload= jwt.decode(data.refresh_token,SECRET_KEY,algorithms=[ALGORITHM])

     except JWTError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token or token expired")
     
     #checktoken type
     if playload.get('type')!='refresh':
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid refresh token')
     
     #token detail

     jti=playload.get('jti')
     family_id=playload.get('family_id')
     user_id=playload.get('user_id')
     if not jti or not family_id or not user_id:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")
     
     #Check whether the family is revoked
     revoked_family=db.query(RevokedTokenFamily).filter(RevokedTokenFamily.family_id == family_id).first()
     if revoked_family is not None:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")

     #check is this token is already used
     revoked=db.query(RevokedToken).filter( RevokedToken.jti == jti).first()
     if revoked is not None:
          # Reuse detected:- revoke this login session
          db.add(RevokedTokenFamily(family_id=family_id))
          db.commit()
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Refresh token reuse detected; session revoked')
     
     # Create replacement tokens with the same family ID
     new_access_token=create_access_token({'user_id':user_id,'type':"access"})
     new_refresh_token=create_refresh_token({'user_id':user_id,'family_id':family_id})

     # Revoke the old refresh token
     db.add(RevokedToken(jti=jti))
     db.commit()

     return{
          'access_token':new_access_token,
          'refresh_token':new_refresh_token,
          'type':"bearer"
     }


@router.post("/logout")
@limiter.limit('10/minute')
def logout(request:Request,data:RefreshToken,db:Session=Depends(get_db)):
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
@limiter.limit('5/minute')
def login(request:Request,user_detail:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
     print("USERNAME:", user_detail.username)
     print("PASSWORD RECEIVED:", bool(user_detail.password))
     user=db.query(User).filter(User.username == user_detail.username).first()

     print("USER FOUND:", user is not None)

     if user is not None:
          if verify_hash(user_detail.password,user.password):
               family_id=str(uuid4())
               access_token = create_access_token({"user_id": user.id,"type": "access"})
               refresh_token = create_refresh_token({"user_id": user.id,"family_id":family_id})
               return {
                    "Message":"Login Successfull",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "Token_type":"bearer"
               }
          raise HTTPException(status_code=401,detail="Invalid email or password")
     raise HTTPException(status_code=401,detail="Invalid email or password")