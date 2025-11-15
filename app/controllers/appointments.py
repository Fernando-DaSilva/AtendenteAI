from fastapi import APIRouter, Depends
from database import get_db
from models import Appointment
from schemas import AppointmentCreate

router = APIRouter()

@router.post("/")
def create_appointment(payload: AppointmentCreate, db=Depends(get_db)):
    ap = Appointment(**payload.dict())
    db.add(ap)
    db.commit()
    db.refresh(ap)
    return ap
