from tortoise import fields, models
from enum import Enum

class UserRole(str, Enum):
    EMPLOYER = "employer"
    SEEKER = "seeker"
    ADMIN = "admin"

class VacancyStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class PromotionTier(str, Enum):
    STANDARD = "standard"
    PRO = "pro"
    VIP = "vip"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    INTERVIEW = "interview"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class User(models.Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, null=True)
    email = fields.CharField(max_length=255, unique=True, null=True)
    full_name = fields.CharField(max_length=255)
    role = fields.CharEnumField(UserRole, default=UserRole.SEEKER)
    country = fields.CharField(max_length=100, default="Kazakhstan")
    city = fields.CharField(max_length=100, default="Almaty")
    hashed_password = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

class Vacancy(models.Model):
    id = fields.IntField(pk=True)
    employer = fields.ForeignKeyField("models.User", related_name="vacancies")
    title = fields.CharField(max_length=255)
    category = fields.CharField(max_length=100)
    salary = fields.CharField(max_length=100)
    salary_currency = fields.CharField(max_length=10, default="KZT")
    location = fields.CharField(max_length=255)
    description = fields.TextField()
    requirements = fields.TextField(null=True)
    status = fields.CharEnumField(VacancyStatus, default=VacancyStatus.OPEN)
    is_vip = fields.BooleanField(default=False)
    promotion_tier = fields.CharEnumField(PromotionTier, default=PromotionTier.STANDARD)
    premium_till = fields.DatetimeField(null=True)
    lat = fields.FloatField(null=True)
    lng = fields.FloatField(null=True)
    instagram_card_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vacancies"

class CV(models.Model):
    id = fields.IntField(pk=True)
    seeker = fields.OneToOneField("models.User", related_name="cv")
    full_name = fields.CharField(max_length=255)
    experience = fields.TextField()
    skills = fields.TextField()
    photo_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "cvs"

class CompanyProfile(models.Model):
    id = fields.IntField(pk=True)
    employer = fields.OneToOneField("models.User", related_name="company_profile")
    company_name = fields.CharField(max_length=255)
    description = fields.TextField()
    website = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "company_profiles"

class Application(models.Model):
    id = fields.IntField(pk=True)
    seeker = fields.ForeignKeyField("models.User", related_name="applications")
    vacancy = fields.ForeignKeyField("models.Vacancy", related_name="applications")
    cover_letter = fields.TextField(null=True)
    status = fields.CharEnumField(ApplicationStatus, default=ApplicationStatus.PENDING)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "applications"

class Transaction(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="transactions")
    vacancy = fields.ForeignKeyField("models.Vacancy", related_name="transactions", null=True)
    amount = fields.IntField()
    currency = fields.CharField(max_length=10, default="KZT")
    status = fields.CharEnumField(TransactionStatus, default=TransactionStatus.PENDING)
    external_id = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "transactions"

class ChatRoom(models.Model):
    id = fields.IntField(pk=True)
    candidate = fields.ForeignKeyField("models.User", related_name="candidate_rooms")
    employer = fields.ForeignKeyField("models.User", related_name="employer_rooms")
    vacancy = fields.ForeignKeyField("models.Vacancy", related_name="chat_rooms")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_rooms"
        unique_together = (("candidate", "employer", "vacancy"),)

class Message(models.Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField("models.ChatRoom", related_name="messages")
    sender = fields.ForeignKeyField("models.User", related_name="sent_messages")
    content = fields.TextField()
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "messages"
