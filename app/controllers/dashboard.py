import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db)) -> List[dict]:
    """
    List all active conversations.
    """
    try:
        conversations = db.query(Conversation).all()
        return [
            {
                "id": c.id,
                "lead_id": c.lead_id,
                "status": c.status,
                "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None
            }
            for c in conversations
        ]
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/conversations/{cid}")
def get_conversation(cid: int, db: Session = Depends(get_db)) -> List[dict]:
    """
    Get all messages in a conversation.
    
    Args:
        cid: Conversation ID
        db: Database session
        
    Returns:
        List of messages
    """
    try:
        messages = db.query(Message).filter_by(conversation_id=cid).all()
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None
            }
            for m in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {cid}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
