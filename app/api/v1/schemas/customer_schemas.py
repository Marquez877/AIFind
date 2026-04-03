from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerCreateRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None
    company: str | None = None


class CustomerUpdateRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str | None
    company: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
