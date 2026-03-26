from fastapi import APIRouter, HTTPException, Depends
from models import User, Vacancy, Transaction, TransactionStatus, PromotionTier
from pydantic import BaseModel
from typing import Optional
import datetime

router = APIRouter(prefix="/payments", tags=["payments"])

class CreatePaymentRequest(BaseModel):
    user_id: int
    vacancy_id: Optional[int] = None
    amount: int
    plan_name: str # 'standard', 'pro', 'vip'

@router.post("/create-session")
async def create_payment_session(data: CreatePaymentRequest):
    user = await User.get_or_none(id=data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    vacancy = None
    if data.vacancy_id:
        vacancy = await Vacancy.get_or_none(id=data.vacancy_id)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")
            
    transaction = await Transaction.create(
        user=user,
        vacancy=vacancy,
        amount=data.amount,
        status=TransactionStatus.PENDING,
        external_id=f"PAY-{data.plan_name.upper()}-{int(datetime.datetime.now().timestamp())}"
    )
    
    # Mock redirect URL - In a real app this would be Stripe/Kaspi URL
    return {
        "checkout_url": f"/checkout/{transaction.external_id}",
        "transaction_id": transaction.id,
        "external_id": transaction.external_id
    }

@router.post("/verify/{external_id}")
async def verify_payment(external_id: str):
    transaction = await Transaction.get_or_none(external_id=external_id).prefetch_related("user", "vacancy")
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.status == TransactionStatus.COMPLETED:
        return {"message": "Already completed", "status": "success"}

    # Simulate successful payment logic
    transaction.status = TransactionStatus.COMPLETED
    await transaction.save()
    
    # If it's a vacancy promotion, update the vacancy status
    if transaction.vacancy:
        # Determine tier from external_id or amount
        tier = PromotionTier.STANDARD
        if "PRO" in transaction.external_id:
            tier = PromotionTier.PRO
        elif "VIP" in transaction.external_id:
            tier = PromotionTier.VIP
            transaction.vacancy.is_vip = True
            
        transaction.vacancy.promotion_tier = tier
        # Set premium for 30 days
        transaction.vacancy.premium_till = datetime.datetime.now() + datetime.timedelta(days=30)
        await transaction.vacancy.save()
        
    return {"message": "Payment verified successfully", "status": "success"}
