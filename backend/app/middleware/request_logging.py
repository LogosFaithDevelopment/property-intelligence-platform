"""
Request logging middleware for FastAPI
Tracks request IDs, duration, and logs all requests/responses
"""

import time
import uuid
from typing import Callable

from app.utils.logging_config import get_logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    Adds request ID tracking and duration measurement
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Extract request details
        method = request.method
        url = str(request.url)
        endpoint = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            f"Incoming request: {method} {endpoint}",
            extra={
                'request_id': request_id,
                'method': method,
                'endpoint': endpoint,
                'extra_data': {
                    'url': url,
                    'client_ip': client_host,
                    'user_agent': request.headers.get('user-agent', 'unknown')
                }
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log response
            logger.info(
                f"Request completed: {method} {endpoint} - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration even for errors
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            logger.error(
                f"Request failed: {method} {endpoint}",
                exc_info=True,
                extra={
                    'request_id': request_id,
                    'method': method,
                    'endpoint': endpoint,
                    'duration_ms': duration_ms,
                    'extra_data': {
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                }
            )
            
            # Re-raise exception to be handled by exception handlers
            raise
