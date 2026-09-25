from fastapi import APIRouter

from .auth import router as auth_router
from .incidents import router as incident_router
from .services import router as service_router
from .teams import router as team_router
from .users import router as user_router

api_router = APIRouter()

api_router.include_router(incident_router)
api_router.include_router(service_router)
api_router.include_router(team_router)
api_router.include_router(user_router)
api_router.include_router(auth_router)
