from fastapi import APIRouter
from fastapi import File,UploadFile
from fastapi import BackgroundTasks
from typing import List
from fastapi import HTTPException
import os
from fastapi import Header
from fast_app.models.post import Post
from fast_app.utils.auth import get_current_user
from sqlalchemy.orm import Session
from fast_app.database.database import get_db
from fastapi import Depends

# BackGroundTask...........
router=APIRouter()

def write_log(username: str):
    with open("log.txt", "a") as file:
        file.write(f"User {username} registered\n")


@router.post("/test-background")
def test_background(
    username: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, username)

    return {"message": "Request completed"}

#single fileUpload

@router.post('/upload-single-file')
async def upload_file(file:UploadFile=File()):
    os.makedirs("fast_app/uploads", exist_ok=True)
    contents=await file.read()
    with open(f"fast_app/uploads/{file.filename}", "wb") as f:
        f.write(contents)
    return{
        "Msg":"file uploaded",
        "Filename":file.filename,
        "content_type":file.content_type
    }

@router.post("/upload-multiple-file")
async def mul(files:List[UploadFile]=File()):
    return{
        "files":[file.filename for file in files]
    }

@router.post("/valid-file")
async def valid(file:UploadFile=File()):
    contents=await file.read()
    if file.content_type not in['image/jpeg',"image/png"]:
        raise HTTPException(status_code=400,detail="only png and jpeg allowed to upload")

@router.post("/user_agent")
def user(user_agent:str |None =Header(default=None)):
    return{
        "user":user_agent
    }

from fastapi import Cookie
from fastapi import Response
@router.get("/set-cookie")
def set_cookie(response:Response):
    response.set_cookie(key='Username',value="Thoufeeq")
    return {"Cookie set":"cookie has been set successfully"}

@router.get("/pg")
def get_pg(Username:str|None=Cookie(default=None)):
    return{
        "username":Username,
        "posts":"take a look username got from cookies",

    }

@router.post("/transaction")
#Here we dont need to add db.commit or db.rollback just db.add_all([post1,post2])
def trans(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    with db.begin():
        Post1=Post(
            title="20's life ",
            content="This is stage of life where you will figureout what to do and what not......",
            author_id=current_user.id
        )
        Post2=Post(
            title="5-places you must be quite",
            content="Being quite a places where your words have no effect or attention towards you....",
            author_id=current_user.id
        )
        db.add_all([Post1,Post2])
        return {
            "Message":"Successfully posts saved"
        }
    