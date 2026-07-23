from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logger import logger

class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)

async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.message}", extra={"status_code": exc.status_code})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.message}}
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"message": "Internal Server Error"}}
    )
