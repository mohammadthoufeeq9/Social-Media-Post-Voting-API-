from fastapi import FastAPI
from fast_app.router import posts,profile,practice,auth_log,vote
from fast_app.utils.auth import get_current_user
import time
from fastapi import Request
from slowapi import _rate_limit_exceeded_handler
from fast_app.utils.rate_limit import limiter
from slowapi.errors import RateLimitExceeded


app=FastAPI()

app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

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
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = ( "camera=(), microphone=(), geolocation=()")

    #Return response
    return response



