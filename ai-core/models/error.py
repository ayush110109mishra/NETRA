"""
Structured error response schemas for NETRA API.
Guarantees clean, typed, user-safe error responses without raw stack trace leaks.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class APIError(BaseModel):
    """Structured error payload."""
    code: str = Field(..., description="Machine-readable error code (e.g. INVALID_INPUT, NOT_FOUND)")
    message: str = Field(..., description="Human-readable explanation of the error")
    field: Optional[str] = Field(default=None, description="Field path that triggered the error, if applicable")
    details: Optional[Any] = Field(default=None, description="Additional contextual details")


class APIErrorResponse(BaseModel):
    """Top-level error response envelope."""
    error: APIError
