from fastapi import APIRouter, Request, Depends
from database import get_db
from models import Lead, Conversation, Message
from workers.process_message import process_message
from services.twilio_service import send_whatsapp

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, db=Depends(get_db)):
    data = await request.form()
    sender = data.get("From")
    text = data.get("Body")

    # get or create lead
    lead = db.query(Lead).filter_by(phone=sender).first()
    if not lead:
        lead = Lead(phone=sender)
        db.add(lead)
        db.commit()
        db.refresh(lead)

    # get or create conversation
    conv = db.query(Conversation).filter_by(lead_id=lead.id, status="open").first()
    if not conv:
        conv = Conversation(lead_id=lead.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # store message
    msg = Message(conversation_id=conv.id, sender="lead", content=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # send to worker
    process_message.delay(conv.id, msg.id)

    return "OK"
