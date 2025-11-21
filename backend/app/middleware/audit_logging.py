"""
Audit logging middleware for security and compliance
Logs all API requests with user context, IP addresses, and outcomes
"""
import logging
import json
import time
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.config import settings

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# File handler for audit logs
audit_file_handler = logging.FileHandler("logs/audit.log")
audit_file_handler.setLevel(logging.INFO)

# JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

audit_file_handler.setFormatter(JSONFormatter())
audit_logger.addHandler(audit_file_handler)

# Also log to console in development
if not settings.is_production:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    audit_logger.addHandler(console_handler)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests for audit trail
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health checks and static files
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        start_time = time.time()

        # Extract request details
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Get user from request state (set by auth middleware when implemented)
        user_id = getattr(request.state, "user_id", "anonymous")

        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log successful request
            audit_logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                extra={
                    "event_type": "api_request",
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "user_id": user_id,
                    "status_code": response.status_code,
                    "duration_seconds": round(duration, 3),
                    "success": response.status_code < 400
                }
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Log failed request
            audit_logger.error(
                f"{request.method} {request.url.path} - ERROR: {str(e)}",
                extra={
                    "event_type": "api_request_error",
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "user_id": user_id,
                    "error": str(e),
                    "duration_seconds": round(duration, 3),
                    "success": False
                }
            )

            # Re-raise exception
            raise


def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
    """
    Log security-relevant events

    Args:
        event_type: Type of security event (e.g., "file_upload", "ai_analysis", "authentication_failure")
        details: Dict of event details
        severity: Log severity (INFO, WARNING, ERROR, CRITICAL)
    """
    log_data = {
        "event_type": f"security_{event_type}",
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }

    log_func = getattr(audit_logger, severity.lower(), audit_logger.info)
    log_func(f"Security Event: {event_type}", extra=log_data)
