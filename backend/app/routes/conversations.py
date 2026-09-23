# backend/app/routes/conversations.py
"""
Routes pour la persistance des conversations du chatbot.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from app.database import get_db, Conversation, Message

router = APIRouter(prefix="/conversations", tags=["Conversations"])


# ============================================================
# SCHEMAS
# ============================================================
class ConversationCreate(BaseModel):
    title: Optional[str] = "Nouvelle conversation"
    user_id: Optional[str] = "default"


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    pinned: Optional[bool] = None


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class ConversationOut(BaseModel):
    id: str
    title: str
    pinned: bool
    created_at: str
    updated_at: str
    message_count: int


class ConversationDetail(BaseModel):
    id: str
    title: str
    pinned: bool
    created_at: str
    updated_at: str
    messages: List[MessageOut]


# ============================================================
# ROUTES
# ============================================================
@router.get("/", response_model=List[ConversationOut])
async def list_conversations(user_id: str = "default", db: Session = Depends(get_db)):
    """Liste toutes les conversations (épinglées en premier)."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.pinned.desc(), Conversation.updated_at.desc())
        .all()
    )
    result = []
    for c in convs:
        msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        result.append(ConversationOut(
            id=c.id,
            title=c.title,
            pinned=bool(c.pinned),
            created_at=c.created_at.isoformat() if c.created_at else "",
            updated_at=c.updated_at.isoformat() if c.updated_at else "",
            message_count=msg_count,
        ))
    return result


@router.post("/", response_model=ConversationOut)
async def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle conversation."""
    conv_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow()
    conv = Conversation(
        id=conv_id,
        user_id=data.user_id,
        title=data.title or "Nouvelle conversation",
        pinned=0,
        created_at=now,
        updated_at=now,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationOut(
        id=conv.id,
        title=conv.title,
        pinned=bool(conv.pinned),
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        message_count=0,
    )


@router.get("/{conv_id}", response_model=ConversationDetail)
async def get_conversation(conv_id: str, db: Session = Depends(get_db)):
    """Récupère une conversation avec tous ses messages."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        pinned=bool(conv.pinned),
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
            for m in messages
        ],
    )


@router.post("/{conv_id}/messages", response_model=MessageOut)
async def add_message(conv_id: str, data: MessageCreate, db: Session = Depends(get_db)):
    """Ajoute un message à une conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    msg = Message(
        conversation_id=conv_id,
        role=data.role,
        content=data.content,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()

    # Auto-titre si premier message utilisateur
    if data.role == "user" and conv.title == "Nouvelle conversation":
        conv.title = data.content[:40] + ("..." if len(data.content) > 40 else "")

    db.commit()
    db.refresh(msg)
    return MessageOut(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        created_at=msg.created_at.isoformat(),
    )


@router.patch("/{conv_id}", response_model=ConversationOut)
async def update_conversation(conv_id: str, data: ConversationUpdate, db: Session = Depends(get_db)):
    """Met à jour une conversation (titre ou épingle)."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if data.title is not None:
        conv.title = data.title[:100]
    if data.pinned is not None:
        conv.pinned = 1 if data.pinned else 0
    conv.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(conv)
    msg_count = db.query(Message).filter(Message.conversation_id == conv_id).count()
    return ConversationOut(
        id=conv.id,
        title=conv.title,
        pinned=bool(conv.pinned),
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        message_count=msg_count,
    )


@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str, db: Session = Depends(get_db)):
    """Supprime une conversation et tous ses messages."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    db.query(Message).filter(Message.conversation_id == conv_id).delete()
    db.delete(conv)
    db.commit()
    return {"message": "Conversation supprimée", "id": conv_id}