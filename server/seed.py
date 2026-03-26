import asyncio
from tortoise import Tortoise, run_async
from models import User, UserRole, Vacancy, VacancyStatus
import os

async def seed():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()

    # Create Employers
    emp1, _ = await User.get_or_create(
        email="hr@technova.kg",
        defaults={
            "full_name": "TechNova Solutions", 
            "role": UserRole.EMPLOYER,
            "country": "Kazakhstan",
            "city": "Almaty"
        }
    )
    emp2, _ = await User.get_or_create(
        email="jobs@dataflow.kg",
        defaults={
            "full_name": "DataFlow Systems", 
            "role": UserRole.EMPLOYER,
            "country": "Kyrgyzstan",
            "city": "Bishkek"
        }
    )

    # Create Vacancies
    vacancies = [
        {
            "employer": emp1,
            "title": "Senior React Developer",
            "category": "Программирование",
            "salary": "450,000",
            "salary_currency": "KZT",
            "location": "Алматы",
            "description": "Мы ищем опытного React разработчика.",
            "is_vip": True
        },
        {
            "employer": emp2,
            "title": "Python FastAPI Backend",
            "category": "Программирование",
            "salary": "120,000",
            "salary_currency": "KGS",
            "location": "Бишкек",
            "description": "Разработка API на FastAPI.",
            "is_vip": True
        }
    ]

    for vac_data in vacancies:
        await Vacancy.create(**vac_data)

    print("Database seeded successfully with international data!")

if __name__ == "__main__":
    run_async(seed())
