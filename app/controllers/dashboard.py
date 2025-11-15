from fastapi import APIRouter, Depends
from database import get_db
from models import Conversation, Message

router = APIRouter()

@router.get("/conversations")
def list_conversations(db=Depends(get_db)):
    return db.query(Conversation).all()


@router.get("/conversations/{cid}")
def get_conversation(cid: int, db=Depends(get_db)):
    return db.query(Message).filter_by(conversation_id=cid).all()
