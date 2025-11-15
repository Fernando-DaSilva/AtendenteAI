from workers.celery_app import celery_app
from core.llm import analyze_message, generate_reply
from core.calendar import get_available_slots, create_event
from services.twilio_service import send_whatsapp
from database import SessionLocal
from models import Lead, Conversation, Message


@celery_app.task
def process_message(conversation_id, message_id):
    db = SessionLocal()

    msg = db.query(Message).filter_by(id=message_id).first()
    conv = db.query(Conversation).filter_by(id=conversation_id).first()
    lead = db.query(Lead).filter_by(id=conv.lead_id).first()

    nlu = analyze_message(msg.content)

    reply = None

    if "missing_slots" in nlu:
        reply = generate_reply("ask_slot", nlu)
    else:
        slots = get_available_slots(nlu)
        event = create_event(slots[0], lead, nlu)
        reply = generate_reply("confirm", slots)

    send_whatsapp(lead.phone, reply)

    db.close()
