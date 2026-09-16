"""Payment callbacks are disabled until a real provider verifier is configured.

Do not register test-success or internal balance callbacks as public routes.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/payment/webhook", tags=["payment"])
