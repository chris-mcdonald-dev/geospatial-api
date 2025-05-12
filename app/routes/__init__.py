from app.routes.aggregates import router as aggregates_router
from app.routes.patterns import router as patterns_router
from fastapi import APIRouter

router = APIRouter()
routers = [
    aggregates_router,
    patterns_router,
]

for route in routers:
    router.include_router(route)