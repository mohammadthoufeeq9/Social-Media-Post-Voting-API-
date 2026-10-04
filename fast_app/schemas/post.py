from pydantic import BaseModel,ConfigDict,EmailStr
from datetime import datetime


class update_post(BaseModel):#patch needs to omite few things so we create another schema with a none
     title:str | None=None
     content:str|None=None

class create_post(BaseModel):
    title:str
    content:str

class PostResponse(BaseModel):
    id:int
    title:str
    content:str
    published:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class PostsResponse(BaseModel):#_list_post
    Message:str
    notify:bool
    Posts:list[PostResponse]

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class ProfileUpdate(BaseModel):
    username:str|None=None
    email:EmailStr|None=None

class PasswordChange(BaseModel):
    current_password:str
    New_password:str

class UserNotFoundException(Exception):
    pass