from typing import List

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_audit_repository
from app.repo import AuditLogRepository
from app.schemas.responses.models.transaction_responses import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=List[AuditLogResponse])
def get_all_audit_logs(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        audit_repo: AuditLogRepository = Depends(get_audit_repository)
):
    """Get recent audit logs across all transactions (paginated)."""
    logs = audit_repo.get_recent_logs(limit)

    if skip > 0:
        logs = logs[skip:]

    return logs


__all__ = ['router']
