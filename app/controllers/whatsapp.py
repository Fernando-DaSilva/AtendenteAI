import logging
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Lead, Conversation, Message
from workers.process_message import process_message
from services.twilio_service import send_whatsapp
from core.utils import clean_phone

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive WhatsApp messages via Twilio webhook.
    
    This endpoint:
    1. Extracts sender and message content
    2. Creates or retrieves lead record
    3. Stores message in conversation
    4. Queues message for async processing
    """
    try:
        data = await request.form()
        sender = data.get("From", "").strip()
        text = data.get("Body", "").strip()
        
        # Validate inputs
        if not sender or not text:
            logger.warning("Missing sender or text in webhook data")
            raise HTTPException(status_code=400, detail="Missing sender or message body")
        
        # Clean phone number
        clean_sender = clean_phone(sender)
        logger.info(f"Received message from {clean_sender}: {text[:50]}...")
        
        # Get or create lead
        lead = db.query(Lead).filter_by(phone=clean_sender).first()
        if not lead:
            lead = Lead(phone=clean_sender)
            db.add(lead)
            db.commit()
            db.refresh(lead)
            logger.info(f"Created new lead: {clean_sender}")
        
        # Get or create open conversation
        conv = db.query(Conversation).filter_by(lead_id=lead.id, status="open").first()
        if not conv:
            conv = Conversation(lead_id=lead.id)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            logger.info(f"Created new conversation for lead {lead.id}")
        
        # Store incoming message
        msg = Message(conversation_id=conv.id, sender="lead", content=text)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        logger.info(f"Stored message {msg.id} in conversation {conv.id}")
        
        # Queue async processing
        process_message.delay(conv.id, msg.id)
        logger.info(f"Queued message {msg.id} for processing")
        
        return {"status": "received", "message_id": msg.id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
