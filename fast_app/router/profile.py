from fastapi import HTTPException,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.schemas.post import(
     UserResponse,PasswordChange,ProfileUpdate,
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import get_current_user

from fastapi import Request
from fast_app.utils.rate_limit import limiter

router = APIRouter()


@router.get("/my-profile",response_model= UserResponse)
def get_profile(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return current_user


@router.patch("/update-profile",response_model=UserResponse)
@limiter.limit("5/minute")
def profile_update_of_user(request:Request,profile_data:ProfileUpdate,current_user=Depends(get_current_user),data:Session=Depends(get_db)):
    if profile_data.username is not None:
        current_user.username = profile_data.username
    if profile_data.email is not None:
        current_user.email = profile_data.email
    if profile_data.Bio is not None:
        current_user.Bio = profile_data.Bio

    data.commit()
    data.refresh(current_user)

    return current_user


@router.put("/chnage-password")
@limiter.limit("5/minute")
def change_password(request:Request,pass_change:PasswordChange,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    if not verify_hash(pass_change.current_password,current_user.password):
        raise HTTPException(status_code=401,detail="Current password is incorrect")
    
    current_user.password = hash_password(pass_change.New_password)

    db.commit()
    return {
        "message": "Password changed successfully"
    }