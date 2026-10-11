from fastapi import FastAPI
from fast_app.router import posts,profile,practice,auth_log,vote
from fast_app.utils.auth import get_current_user
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app=FastAPI()
app.include_router(posts.router,tags=['Posts'])
app.include_router(profile.router,tags=['Profile'])
app.include_router(auth_log.router,tags=['Auth'])
app.include_router(vote.router)
app.include_router(practice.router,tags=['Expermental_route'])

@app.middleware('http')
async def log_request(req:Request, call_next):
    #Before request
    start= time.time()

    #Let the request continue to the endpoint
    response= await call_next(req)

    #After endpoint finishes
    process_time= time.time() -start

    #Do somethin with the result
    print(req.method,req.url.path, f"{process_time:.3f}s")

    #Return response
    return response



