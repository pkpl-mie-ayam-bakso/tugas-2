"""Security utilities for audit logging and IP extraction."""
import logging
from .models import AuditLog

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request.

    Handles proxied requests (X-Forwarded-For header).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit_event(action, request, success=True, changes=None):
    """Log security-relevant events.

    Args:
        action: Event type (UPDATE, VIEW, FAILED_AUTH, etc.)
        request: HTTP request object
        success: Whether action succeeded
        changes: Dictionary of changed fields
    """
    if changes is None:
        changes = {}

    try:
        user_email = (
            request.user.email
            if request.user.is_authenticated
            else 'anonymous'
        )

        AuditLog.objects.create(
            action=action,
            user_email=user_email,
            ip_address=get_client_ip(request),
            changes=changes,
            success=success
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
