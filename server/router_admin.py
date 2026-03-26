from fastapi import APIRouter, HTTPException, Depends
from models import Vacancy, User, UserRole, VacancyStatus
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/moderation", response_model=List[dict])
async def list_pending_vacancies():
    # In a real app, you'd have a 'PENDING' status. 
    # For now, we'll just show all 'OPEN' vacancies.
    vacancies = await Vacancy.all().prefetch_related("employer")
    return [{
        "id": v.id,
        "title": v.title,
        "employer": v.employer.full_name,
        "status": v.status,
        "created_at": v.created_at
    } for v in vacancies]

@router.post("/approve/{vacancy_id}")
async def approve_vacancy(vacancy_id: int):
    vacancy = await Vacancy.get_or_none(id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    vacancy.status = VacancyStatus.OPEN
    await vacancy.save()
    return {"message": "Vacancy approved"}

@router.get("/stats")
async def get_stats():
    user_count = await User.all().count()
    vacancy_count = await Vacancy.all().count()
    return {
        "total_users": user_count,
        "total_vacancies": vacancy_count,
        "revenue": "0 ₸" # Placeholder
    }
