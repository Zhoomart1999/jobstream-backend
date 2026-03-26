from fastapi import APIRouter, HTTPException, Depends
from models import User, UserRole, CV, CompanyProfile, Vacancy, Application
from auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

class CVRequest(BaseModel):
    full_name: str
    experience: str
    skills: str
    photo_url: Optional[str] = None

class CompanyProfileRequest(BaseModel):
    company_name: str
    description: str
    website: Optional[str] = None

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    if user.role == UserRole.EMPLOYER:
        profile = await CompanyProfile.get_or_none(employer=user)
        return {"user": user, "company_profile": profile}
    else:
        cv = await CV.get_or_none(seeker=user)
        return {"user": user, "cv": cv}

@router.post("/candidate/cv")
async def update_cv(data: CVRequest, user: User = Depends(get_current_user)):
    if user.role != UserRole.SEEKER:
        raise HTTPException(status_code=403, detail="Only seekers can have CVs")
    cv, _ = await CV.update_or_create(
        seeker=user,
        defaults={
            "full_name": data.full_name,
            "experience": data.experience,
            "skills": data.skills,
            "photo_url": data.photo_url
        }
    )
    return {"status": "success", "cv": cv}

@router.post("/employer/profile")
async def update_company_profile(data: CompanyProfileRequest, user: User = Depends(get_current_user)):
    if user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can have company profiles")
    profile, _ = await CompanyProfile.update_or_create(
        employer=user,
        defaults={
            "company_name": data.company_name,
            "description": data.description,
            "website": data.website
        }
    )
    return {"status": "success", "company_profile": profile}

@router.get("/employer/vacancies")
async def get_employer_vacancies(user: User = Depends(get_current_user)):
    if user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers")
    vacancies = await Vacancy.filter(employer=user).prefetch_related("applications", "applications__seeker").order_by("-created_at")
    
    result = []
    for v in vacancies:
        apps = []
        for a in v.applications:
             cv = await CV.get_or_none(seeker=a.seeker) if a.seeker else None
             apps.append({
                 "id": a.id,
                 "status": a.status,
                 "candidate_name": cv.full_name if cv else (a.seeker.full_name if a.seeker else "Unknown"),
                 "candidate_id": a.seeker.id if a.seeker else None
             })
        result.append({
            "id": v.id,
            "title": v.title,
            "salary": v.salary,
            "salary_currency": v.salary_currency,
            "location": v.location,
            "status": v.status,
            "applications": apps
        })
    return {"vacancies": result}

@router.get("/candidate/applications")
async def get_candidate_applications(user: User = Depends(get_current_user)):
    if user.role != UserRole.SEEKER:
        raise HTTPException(status_code=403, detail="Only candidates")
    apps = await Application.filter(seeker=user).prefetch_related("vacancy", "vacancy__employer").order_by("-created_at")
    return {
        "applications": [
            {
                "id": a.id, 
                "status": a.status, 
                "vacancy": {
                    "id": a.vacancy.id, 
                    "title": a.vacancy.title,
                    "employer_id": a.vacancy.employer.id,
                }
            } for a in apps
        ]
    }
