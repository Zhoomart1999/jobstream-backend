from fastapi import APIRouter, HTTPException, Depends
from models import User, Vacancy, ChatRoom, Message
from pydantic import BaseModel
from typing import List, Optional
import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageCreate(BaseModel):
    room_id: int
    sender_id: int
    content: str

class RoomCreate(BaseModel):
    candidate_id: int
    employer_id: int
    vacancy_id: int

@router.post("/rooms", response_model=dict)
async def get_or_create_room(data: RoomCreate):
    room, created = await ChatRoom.get_or_create(
        candidate_id=data.candidate_id,
        employer_id=data.employer_id,
        vacancy_id=data.vacancy_id
    )
    return {"id": room.id, "created": created}

@router.get("/rooms/{user_id}", response_model=List[dict])
async def list_user_rooms(user_id: int):
    # Rooms where user is either candidate or employer
    rooms = await ChatRoom.filter(
        models.Q(candidate_id=user_id) | models.Q(employer_id=user_id)
    ).prefetch_related("candidate", "employer", "vacancy")
    
    return [{
        "id": r.id,
        "candidate": r.candidate.full_name,
        "employer": r.employer.full_name,
        "vacancy": r.vacancy.title,
        "last_message": "..." # Could be optimized
    } for r in rooms]

@router.get("/messages/{room_id}", response_model=List[dict])
async def list_messages(room_id: int):
    messages = await Message.filter(room_id=room_id).order_by("created_at")
    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "content": m.content,
        "created_at": m.created_at.isoformat()
    } for m in messages]

@router.post("/messages")
async def send_message(data: MessageCreate):
    message = await Message.create(
        room_id=data.room_id,
        sender_id=data.sender_id,
        content=data.content
    )
    return {"id": message.id, "status": "sent"}

# Helper for cities
@router.get("/cities")
async def get_cities():
    return {
        "Kazakhstan": ["Almaty", "Astana", "Shymkent", "Karaganda"],
        "Russia": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg"],
        "Kyrgyzstan": ["Bishkek", "Osh", "Jalal-Abad"]
    }
