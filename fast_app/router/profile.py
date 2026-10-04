from sqlalchemy import or_,and_
from fastapi import HTTPException,Header,Cookie,Form,File,UploadFile,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post,User

from fast_app.schemas.post import(
     UserResponse,PasswordChange,ProfileUpdate,
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import create_access_token,get_current_user,test_user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()


@router.get("/my-profile",response_model= UserResponse)
def get_profile(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return current_user


@router.post("/update-profile",response_model=UserResponse)
def profile_update_of_user(profile_data:ProfileUpdate,current_user=Depends(get_current_user),data:Session=Depends(get_db)):
    if profile_data.username is not None:
        current_user.username = profile_data.username
    if profile_data.email is not None:
        current_user.email = profile_data.email

    data.commit()
    data.refresh(current_user)

    return current_user


@router.put("/chnage-password")
def change_password(pass_change:PasswordChange,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    if not verify_hash(pass_change.current_password,current_user.password):
        raise HTTPException(status_code=401,detail="Current password is incorrect")
    
    current_user.password = hash_password(pass_change.New_password)

    db.commit()
    return {
        "message": "Password changed successfully"
    }