from fastapi import FastAPI
from fast_app.router import posts,profile

app=FastAPI()
app.include_router(posts.router)
app.include_router(profile.router)
# class create_post(BaseModel):
#     title:str
#     content:str


# @app.get("/user_name")
# def get_user():
#     return 'Thoufeeq'

# @app.get("/dep-test")
# def get_dep(user=Depends(get_user)):
#     return {
#         'user': user
#     }


# @app.get("/header-test")
# def header_test(api_key: str | None = Header(default=None)):
#     return {
#         "api_key": api_key
#     }

# @app.get("/cook")
# def cook_test(session_id:str|None = Cookie(default=None)):
#     return{
#         "sessionid":session_id
#     }

# @app.post("/form")
# def form(user_name:str=Form(),password:str=Form()):
#     return{
#         "username":user_name,
#         "password":password
#     }

# @app.post("/upload")
# def upload(file_up:UploadFile=File()):
#     return{
#         "filename":file_up.filename,
#         "content_type":file_up.content_type
#     }
