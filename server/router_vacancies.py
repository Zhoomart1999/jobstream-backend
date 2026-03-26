from fastapi import APIRouter, HTTPException, Depends
from models import Vacancy, User, UserRole, SavedVacancy, Application
from pydantic import BaseModel
from typing import List, Optional
from utils_image import generate_instagram_card
from auth import get_current_user
import os

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

class VacancyCreate(BaseModel):
    title: str
    category: str
    salary: str
    location: str
    description: str
    requirements: Optional[str] = None
    employer_id: int

from tasks import task_post_to_telegram

@router.post("/", response_model=dict)
async def create_vacancy(data: VacancyCreate):
    employer = await User.get_or_none(id=data.employer_id)
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    
    vacancy = await Vacancy.create(
        employer=employer,
        title=data.title,
        category=data.category,
        salary=data.salary,
        location=data.location,
        description=data.description,
        requirements=data.requirements
    )
    
    # Trigger Instagram card generation (could be backgrounded later)
    upload_dir = "static/cards"
    os.makedirs(upload_dir, exist_ok=True)
    card_path = f"{upload_dir}/vacancy_{vacancy.id}.png"
    
    generate_instagram_card(
        vacancy_title=data.title,
        salary=data.salary,
        company_name=employer.full_name,
        output_path=card_path
    )
    
    vacancy.instagram_card_url = f"/{card_path}"
    await vacancy.save()

    # Trigger background tasks for posting
    task_post_to_telegram.delay(
        title=data.title,
        salary=data.salary,
        location=data.location,
        url=f"https://jobstream.kg/vacancies/{vacancy.id}"
    )
    
    return {"id": vacancy.id, "message": "Vacancy created successfully and queued for posting", "card_url": vacancy.instagram_card_url}

@router.get("/", response_model=List[dict])
async def list_vacancies(
    q: Optional[str] = None,
    location: Optional[str] = None,
    salary_min: Optional[int] = None,
    category: Optional[str] = None
):
    query = Vacancy.all().prefetch_related("employer")
    
    if q:
        query = query.filter(title__icontains=q)
    if location:
        query = query.filter(location__icontains=location)
    if category:
        query = query.filter(category=category)
    # Simple salary filter assuming format "XXX,XXX ₸"
    # In a real app, salary would be an integer field.
    
    vacancies = await query
    
    # Sort VIPs first
    vacancies = sorted(vacancies, key=lambda x: x.is_vip, reverse=True)
    
    return [{
        "id": v.id,
        "title": v.title,
        "employer": v.employer.full_name if v.employer else "Anonymous",
        "salary": v.salary,
        "location": v.location,
        "status": v.status,
        "is_vip": v.is_vip,
        "category": v.category,
        "lat": v.lat or 43.2389,
        "lng": v.lng or 76.8897
    } for v in vacancies]

@router.get("/{id}", response_model=dict)
async def get_vacancy(id: int):
    vacancy = await Vacancy.get_or_none(id=id).prefetch_related("employer")
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    # Increment view count
    vacancy.view_count = (vacancy.view_count or 0) + 1
    await vacancy.save()

    app_count = await Application.filter(vacancy=vacancy).count()

    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "employer": vacancy.employer.full_name if vacancy.employer else "Anonymous",
        "salary": vacancy.salary,
        "location": vacancy.location,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "status": vacancy.status,
        "is_vip": vacancy.is_vip,
        "category": vacancy.category,
        "lat": vacancy.lat,
        "lng": vacancy.lng,
        "view_count": vacancy.view_count,
        "application_count": app_count,
        "created_at": vacancy.created_at.isoformat()
    }

# --- Saved Vacancies ---
@router.post("/{id}/save", response_model=dict)
async def save_vacancy(id: int, user: User = Depends(get_current_user)):
    vacancy = await Vacancy.get_or_none(id=id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    saved, created = await SavedVacancy.get_or_create(user=user, vacancy=vacancy)
    return {"saved": True, "created": created}

@router.delete("/{id}/save", response_model=dict)
async def unsave_vacancy(id: int, user: User = Depends(get_current_user)):
    deleted = await SavedVacancy.filter(user=user, vacancy_id=id).delete()
    return {"saved": False, "deleted": deleted > 0}

@router.get("/saved/list", response_model=List[dict])
async def get_saved_vacancies(user: User = Depends(get_current_user)):
    saved = await SavedVacancy.filter(user=user).prefetch_related("vacancy", "vacancy__employer")
    return [{
        "id": s.vacancy.id,
        "title": s.vacancy.title,
        "employer": s.vacancy.employer.full_name if s.vacancy.employer else "Anonymous",
        "salary": s.vacancy.salary,
        "location": s.vacancy.location,
        "saved_at": s.created_at.isoformat()
    } for s in saved]

class ApplicationCreate(BaseModel):
    candidate_id: int
    message: Optional[str] = ""

@router.post("/{id}/apply", response_model=dict)
async def apply_to_vacancy(id: int, data: ApplicationCreate):
    from models import Application, ChatRoom
    vacancy = await Vacancy.get_or_none(id=id).prefetch_related("employer")
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    candidate = await User.get_or_none(id=data.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    application = await Application.create(
        seeker=candidate,
        vacancy=vacancy,
        cover_letter=data.message
    )
    
    room, _ = await ChatRoom.get_or_create(
        candidate=candidate,
        employer=vacancy.employer,
        vacancy=vacancy
    )
    
    return {"id": application.id, "room": room.id, "message": "Application submitted successfully"}
