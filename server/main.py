from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from router_auth import router as auth_router
from router_vacancies import router as vacancies_router
from router_admin import router as admin_router
from router_payments import router as payments_router
from router_chat import router as chat_router
from router_users import router as users_router

load_dotenv()

app = FastAPI(title="JobStream API")
app.include_router(auth_router)
app.include_router(vacancies_router)
app.include_router(admin_router)
app.include_router(payments_router)
app.include_router(chat_router)
app.include_router(users_router)

# Mount static files for generated Instagram cards
os.makedirs("static/cards", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Tortoise-ORM
register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
async def root():
    return {"message": "JobStream API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
