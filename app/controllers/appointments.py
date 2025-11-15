import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Appointment
from schemas import AppointmentCreate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=dict)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Create a new appointment.
    
    Args:
        payload: Appointment data
        db: Database session
        
    Returns:
        Created appointment
    """
    try:
        ap = Appointment(**payload.dict())
        db.add(ap)
        db.commit()
        db.refresh(ap)
        logger.info(f"Created appointment {ap.id} for lead {ap.lead_id}")
        return {"id": ap.id, "status": ap.status, "service": ap.service}
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def list_appointments(db: Session = Depends(get_db)) -> List[dict]:
    """
    List all appointments.
    """
    try:
        appointments = db.query(Appointment).all()
        return [{"id": a.id, "service": a.service, "status": a.status} for a in appointments]
    except Exception as e:
        logger.error(f"Error listing appointments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
