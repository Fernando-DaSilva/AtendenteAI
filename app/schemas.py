from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    sender: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=10000)

    @validator("sender")
    def validate_sender(cls, v):
        allowed = ["lead", "bot", "human"]
        if v.lower() not in allowed:
            raise ValueError(f"sender must be one of {allowed}")
        return v.lower()


class AppointmentCreate(BaseModel):
    """Schema for creating an appointment."""
    lead_id: int = Field(..., gt=0)
    service: str = Field(..., min_length=1, max_length=100)
    start_at: datetime
    end_at: datetime

    @validator("end_at")
    def validate_end_after_start(cls, v, values):
        if "start_at" in values and v <= values["start_at"]:
            raise ValueError("end_at must be after start_at")
        return v


class AppointmentResponse(BaseModel):
    """Schema for appointment responses."""
    id: int
    lead_id: int
    service: str
    status: str
    start_at: datetime
    end_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for message responses."""
    id: int
    conversation_id: int
    sender: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation responses."""
    id: int
    lead_id: int
    status: str
    last_message_at: Optional[datetime]
    messages: Optional[List[MessageResponse]] = None

    class Config:
        from_attributes = True
