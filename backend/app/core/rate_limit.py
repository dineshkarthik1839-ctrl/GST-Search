import time
from fastapi import Request, HTTPException, status
import redis
from app.core.config import settings

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    decode_responses=True
)

class RateLimiter:
    def __init__(self, times: int = 5, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        
        # We can use a sliding window or simple fixed window. Simple fixed window using INCR and EXPIRE:
        key = f"rate_limit:{path}:{client_ip}"
        
        try:
            current = redis_client.get(key)
            if current and int(current) >= self.times:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
            
            pipe = redis_client.pipeline()
            pipe.incr(key)
            if not current:
                pipe.expire(key, self.seconds)
            pipe.execute()
        except redis.RedisError:
            # If Redis is down, fail open (allow request) to prevent system wide outage
            pass
