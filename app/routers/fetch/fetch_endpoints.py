import logging
import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.celery import celery_app
from app.core.tasks.delete_logs import delete_old_logs
from app.core.tasks.fetch_tasks import (
    sync_single_company_accounts,
    sync_accounts,
    sync_single_company_transactions,
    sync_transactions
)
from app.core.tasks.send_tasks import (
    send_single_company,
    send_all_companies,
    send_single_company_transactions,
    send_all_company_transactions, send_daily_reports
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trigger", tags=["fetch"])


class TaskResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    status_url: str


@router.post("/fetch/accounts/all", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync_all_accounts() -> TaskResponse:
    try:
        task = sync_accounts.delay()
        logger.info(f"✅ Dispatched sync_accounts task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message="Account sync task dispatched successfully for all companies",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch sync_accounts task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/fetch/accounts/{company_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync_company_accounts(company_id: str) -> TaskResponse:
    try:
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid company_id format: {company_id}. Expected UUID."
        )

    try:
        task = sync_single_company_accounts.delay(company_id)
        logger.info(f"✅ Dispatched account sync task for company {company_id}: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message=f"Account sync task dispatched successfully for company {company_id}",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch account sync task for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/fetch/transactions/all", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync_all_transactions() -> TaskResponse:
    try:
        task = sync_transactions.delay()
        logger.info(f"✅ Dispatched sync_transactions task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message="Transaction sync task dispatched successfully for all companies",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch sync_transactions task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/fetch/transactions/{company_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync_company_transactions(company_id: str) -> TaskResponse:
    try:
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid company_id format: {company_id}. Expected UUID."
        )

    try:
        task = sync_single_company_transactions.delay(company_id)
        logger.info(f"✅ Dispatched transaction sync task for company {company_id}: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message=f"Transaction sync task dispatched successfully for company {company_id}",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch transaction sync task for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/send/balances/all", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_send_all_balances() -> TaskResponse:
    try:
        task = send_all_companies.delay()
        logger.info(f"✅ Dispatched send_all_companies task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message="Balance send task dispatched successfully for all companies",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch send_all_companies task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/send/balances/{company_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_send_company_balance(company_id: str) -> TaskResponse:
    try:
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid company_id format: {company_id}. Expected UUID."
        )

    try:
        task = send_single_company.delay(company_id)
        logger.info(f"✅ Dispatched balance send task for company {company_id}: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message=f"Balance send task dispatched successfully for company {company_id}",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch balance send task for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/send/transactions/all", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_send_all_transactions() -> TaskResponse:
    try:
        task = send_all_company_transactions.delay()
        logger.info(f"✅ Dispatched send_all_company_transactions task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message="Transaction send task dispatched successfully for all companies",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch send_all_company_transactions task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/send/transactions/{company_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_send_company_transactions(company_id: str, is_daily: bool = False) -> TaskResponse:
    try:
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid company_id format: {company_id}. Expected UUID."
        )

    try:
        task = send_single_company_transactions.delay(company_id, is_daily)
        logger.info(f"✅ Dispatched transaction send task for company {company_id}: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message=f"Transaction send task dispatched successfully for company {company_id}",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch transaction send task for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/send/report/all", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_send_all_transactions() -> TaskResponse:
    try:
        task = send_daily_reports.delay()
        logger.info(f"✅ Dispatched send_all_company_transactions task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message="Transaction send task dispatched successfully for all companies",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch send_all_company_transactions task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.post("/maintenance/delete-logs", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_delete_old_logs(days: int = 30, batch_size: int = 1000) -> TaskResponse:
    try:
        task = delete_old_logs.delay(days=days, batch_size=batch_size)
        logger.info(f"✅ Dispatched delete_old_logs task: {task.id}")

        return TaskResponse(
            success=True,
            task_id=task.id,
            message=f"Log deletion task dispatched successfully (days={days}, batch_size={batch_size})",
            status_url=f"/fetch/tasks/{task.id}/status"
        )
    except Exception as e:
        logger.error(f"❌ Failed to dispatch delete_old_logs task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch task: {str(e)}"
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    try:
        task = celery_app.AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "state": task.state,
        }

        if task.state == "PENDING":
            response["message"] = "Task is waiting to be processed"
        elif task.state == "PROGRESS":
            response["current"] = task.info.get("current", 0)
            response["total"] = task.info.get("total", 0)
        elif task.state == "SUCCESS":
            response["result"] = task.result
        elif task.state == "FAILURE":
            response["error"] = str(task.info)
            response["traceback"] = task.traceback if hasattr(task, "traceback") else None
        elif task.state == "RETRY":
            response["message"] = "Task is being retried"
            response["retry_count"] = task.info.get("retry_count", 0)

        return response
    except Exception as e:
        logger.error(f"❌ Failed to get task status for {task_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )
