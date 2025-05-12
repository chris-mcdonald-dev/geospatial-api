from fastapi import APIRouter, Depends, Query, HTTPException
from app.constants import DAY_PERIOD_MAPPING
from app.services.pattern_service import PatternService, get_pattern_service

router = APIRouter(prefix="/patterns", tags=["patterns"])

@router.get("/slow_links")
def get_slow_links(
    period: str = Query(..., description="Time period (e.g., AM Peak)"),
    threshold: float = Query(..., description="Average speed threshold"),
    min_days: int = Query(..., description="Minimum number of days below threshold"),
    service: PatternService = Depends(get_pattern_service)
):
    # Input Validation
    if period not in DAY_PERIOD_MAPPING:
        raise HTTPException(status_code=400, detail="Invalid period specified")
    if threshold < 0:
        raise HTTPException(status_code=400, detail="Threshold must be a non-negative number")
    if min_days < 1 or min_days > 7:
        raise HTTPException(status_code=400, detail="Minimum days must be between 1 and 7")

    target_period = DAY_PERIOD_MAPPING[period]

    slow_links_data = service.find_slow_links_data(
        target_period=target_period,
        threshold=threshold,
        min_days=min_days
    )
    
    return slow_links_data