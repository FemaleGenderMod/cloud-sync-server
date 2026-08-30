from datetime import datetime

from pydantic import BaseModel, UUID4


class SuccessResponse(BaseModel):
    success: bool = True


class StatsResponse(BaseModel):
    synced_users: int
    timestamp: datetime


class AuthenticatedResponse(BaseModel):
    success: bool = True
    token: str
    account: UUID4
    expires: datetime


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
