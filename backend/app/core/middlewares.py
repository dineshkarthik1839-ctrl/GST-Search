import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logger import logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        request_id = getattr(request.state, "request_id", "unknown")
        logger.info(f"Incoming Request: {request.method} {request.url.path}", extra={"request_id": request_id})
        
        response: Response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Request Completed: {request.method} {request.url.path} - Status: {response.status_code}", 
            extra={"request_id": request_id, "process_time_ms": round(process_time, 2)}
        )
        return response
