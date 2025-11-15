import logging
from typing import Optional
from workers.celery_app import celery_app
from core.llm import analyze_message, generate_reply
from core.calendar import get_available_slots, create_event
from services.twilio_service import send_whatsapp
from database import SessionLocal
from models import Lead, Conversation, Message

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_message(self, conversation_id: int, message_id: int):
    """
    Process incoming message asynchronously using Celery.
    
    Args:
        conversation_id: ID of the conversation
        message_id: ID of the message to process
    """
    db = None
    try:
        db = SessionLocal()
        
        # Retrieve entities
        msg = db.query(Message).filter_by(id=message_id).first()
        if not msg:
            logger.error(f"Message {message_id} not found")
            return
            
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            logger.error(f"Conversation {conversation_id} not found")
            return
            
        lead = db.query(Lead).filter_by(id=conv.lead_id).first()
        if not lead:
            logger.error(f"Lead for conversation {conversation_id} not found")
            return

        logger.info(f"Processing message {message_id} from lead {lead.phone}")

        # Analyze message using LLM (sync wrapper for async function)
        import asyncio
        try:
            nlu = asyncio.run(analyze_message(msg.content, use_openrouter=True))
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            reply = generate_reply("error", None)
            send_whatsapp(lead.phone, reply)
            return

        # Check if we have all required slots
        reply = None
        missing_slots = nlu.get("missing_slots", [])
        
        if missing_slots and len(missing_slots) > 0:
            reply = generate_reply("ask_slot", nlu)
        else:
            try:
                # All slots filled, proceed with appointment
                slots = get_available_slots(nlu)
                if slots:
                    event = create_event(slots[0], lead, nlu)
                    reply = generate_reply("confirm", slots)
                else:
                    reply = "Desculpe, não há horários disponíveis no momento. Por favor, tente novamente mais tarde. 📅"
            except Exception as e:
                logger.error(f"Calendar/event creation failed: {e}")
                reply = generate_reply("error", None)

        # Send reply via WhatsApp
        if reply:
            send_whatsapp(lead.phone, reply)
            logger.info(f"Reply sent to {lead.phone}: {reply}")

    except Exception as e:
        logger.error(f"Unhandled error in process_message: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        if db:
            db.close()
