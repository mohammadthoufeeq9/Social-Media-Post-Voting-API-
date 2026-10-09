from fastapi import FastAPI
from fast_app.router import posts,profile,noconcern,auth_log,vote
from fast_app.utils.auth import get_current_user
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fast_app.schemas.post import UserNotFoundException

app=FastAPI()
app.include_router(posts.router,tags=['Posts'])
app.include_router(profile.router,tags=['Profile'])
app.include_router(noconcern.router,tags=['Expermental_route'])
app.include_router(auth_log.router,tags=['Auth'])
app.include_router(vote.router)
# app.dependency_overrides[get_current_user]=test_user


#Middleware --Middleware is code that runs before and/or after every request
@app.middleware('http')
async def log_request(req:Request, call_next):
    #Before request
    start= time.time()

    #Let the request continue to the endpoint
    response= await call_next(req)

    #After endpoint finishes
    process_time= time.time() -start

    #Do somethin with the result
    print(req.method,req.url.path, process_time)

    #Return response
    return response

#CORS-corss origin resource sharing 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#"*"-> should be the frontend like "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],# methods like get post....,
    allow_headers=["*"]# headers like /login and all.....
)


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "message": "User not found"
        }
    )

