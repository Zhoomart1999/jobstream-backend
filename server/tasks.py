from celery import Celery
import os
from dotenv import load_dotenv
import asyncio
from bot import post_vacancy_to_channel

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

@celery_app.task
def task_post_to_telegram(title, salary, location, url):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(post_vacancy_to_channel(title, salary, location, url))

@celery_app.task
def task_post_to_instagram(vacancy_id, card_path):
    # This would involve Meta Graph API
    print(f"Posting card {card_path} for vacancy {vacancy_id} to Instagram...")
    return True
