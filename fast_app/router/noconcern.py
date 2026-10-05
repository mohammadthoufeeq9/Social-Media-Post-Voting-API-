from fastapi import APIRouter
from fastapi import File,UploadFile
from fastapi import BackgroundTasks
from typing import List
from fastapi import HTTPException
import os
from fastapi import Header

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
        "posts":"take a look username got from cookies"
    }