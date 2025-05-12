from fastapi import APIRouter, Depends, Query, HTTPException
from app import schemas
from app.constants import DAY_MAPPING, DAY_PERIOD_MAPPING
from app.services.aggregate_service import AggregateService, get_aggregate_service

router = APIRouter(prefix="/aggregates", tags=["aggregates"])

@router.get("/{link_id}")
def get_single_link_aggregate(
    link_id: int,
    day: str = Query(..., description="Day of the week (e.g., Monday)"),
    period: str = Query(..., description="Time period (e.g., AM Peak)"),
    service: AggregateService = Depends(get_aggregate_service)
):
    if day not in DAY_MAPPING or period not in DAY_PERIOD_MAPPING:
        raise HTTPException(status_code=400, detail="Invalid day or period specified")

    target_day_of_week = DAY_MAPPING[day]
    target_period = DAY_PERIOD_MAPPING[period]

    result_dict = service.get_single_link_aggregate_data(
        link_id=link_id,
        target_day_of_week=target_day_of_week,
        target_period=target_period
    )

    if result_dict is None:
        raise HTTPException(status_code=404, detail=f"Data not found for link_id {link_id} on {day} during {period}")
    
    return result_dict

@router.get("/")
def get_all_aggregates(
    day: str = Query(..., description="Day of the week (e.g., Monday)"),
    period: str = Query(..., description="Time period (e.g., AM Peak)"),
    service: AggregateService = Depends(get_aggregate_service)
):
    if day not in DAY_MAPPING or period not in DAY_PERIOD_MAPPING:
        raise HTTPException(status_code=400, detail="Invalid day or period specified")

    target_day_of_week = DAY_MAPPING[day]
    target_period = DAY_PERIOD_MAPPING[period]

    results_list = service.get_all_aggregates_data(
        target_day_of_week=target_day_of_week,
        target_period=target_period
    )
    return results_list

@router.post("/spatial_filter")
def get_spatial_filtered_aggregates(
    request_body: schemas.SpatialFilterRequest, 
    service: AggregateService = Depends(get_aggregate_service)
):
    if request_body.period not in DAY_PERIOD_MAPPING or request_body.day not in DAY_MAPPING:
        raise HTTPException(status_code=400, detail="Invalid day or period specified")

    target_day_of_week = DAY_MAPPING[request_body.day]
    target_period = DAY_PERIOD_MAPPING[request_body.period]
    
    if not isinstance(request_body.bbox, list) or len(request_body.bbox) != 4: # Basic bbox structure check remains in route
        raise HTTPException(status_code=400, detail="Invalid bbox format. Must be a list of 4 floats [x1, y1, x2, y2]")

    try:
        results_list = service.get_spatially_filtered_aggregates_data(
            target_day_of_week=target_day_of_week,
            target_period=target_period,
            bbox_coords=request_body.bbox
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return results_list