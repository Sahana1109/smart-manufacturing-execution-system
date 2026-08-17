import uuid
import json
import logging
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit_logs.models import AuditLog

logger = logging.getLogger(__name__)


async def log_audit_event(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: str,
    user_id: Optional[uuid.UUID] = None,
    details: Optional[Any] = None
) -> AuditLog:
    """
    Creates an immutable audit log entry for enterprise traceability.
    """
    details_str: Optional[str] = None
    if details is not None:
        if isinstance(details, (dict, list)):
            details_str = json.dumps(details, default=str)
        else:
            details_str = str(details)

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details_str,
    )
    db.add(audit_entry)
    # We do not commit immediately to allow inclusion within the calling transaction
    logger.info(f"[AUDIT] Action: '{action}', Entity: '{entity_type}:{entity_id}', User: '{user_id}'")
    return audit_entry
