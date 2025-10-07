from fastapi import APIRouter
from datetime import datetime

api_router = APIRouter()


@api_router.get("/")
async def root():
    return {"message": "Welcome to Futurisys ML API"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
