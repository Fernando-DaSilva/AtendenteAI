from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    sender: str
    content: str


class AppointmentCreate(BaseModel):
    lead_id: int
    service: str
    start_at: datetime
    end_at: datetime
