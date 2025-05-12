from fastapi import Depends
from app.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app import models
from geoalchemy2.functions import ST_AsGeoJSON
import json
from typing import List, Dict, Any

class PatternService:
    def __init__(self, db: Session):
        self.db = db

    def find_slow_links_data(
        self,
        target_period: int,
        threshold: float,
        min_days: int
    ) -> List[Dict[str, Any]]:

        daily_average_speed = (
            select(
                models.SpeedRecord.link_id,
                models.SpeedRecord.day_of_week,
                func.avg(models.SpeedRecord.average_speed).label('average_speed')
            )
            .where(models.SpeedRecord.period == target_period)
            .group_by(models.SpeedRecord.link_id, models.SpeedRecord.day_of_week)
            .subquery("daily_average_speed") # Name the first CTE
        )

        # Filter daily averages below the threshold and check how many slow days each link has
        amount_of_slow_days = (
            select(
                daily_average_speed.c.link_id,
                func.count().label('slow_day_count')
            )
            .where(daily_average_speed.c.average_speed < threshold) # Filter daily averages by threshold
            .group_by(daily_average_speed.c.link_id)
            .having(func.count() >= min_days) # Filter links by minimum slow days
            .subquery("amount_of_slow_days")
        )

        # Match it back up with the Link table
        stmt = select(
            models.Link.link_id,
            models.Link.road_name,
            ST_AsGeoJSON(models.Link.geometry).label('geometry'),
            models.Link.length,
            amount_of_slow_days.c.slow_day_count
        ).join(
            amount_of_slow_days, models.Link.link_id == amount_of_slow_days.c.link_id
        )
        
        results = self.db.execute(stmt).all()

        # Format the response
        formatted_slow_links = []
        for result in results:
            slow_link_dict = {
                "link_id": result.link_id,
                "road_name": result.road_name,
                "geometry": json.loads(result.geometry) if result.geometry else None,
                "length": result.length,
                "slow_day_count": result.slow_day_count,
            }
            formatted_slow_links.append(slow_link_dict)

        return formatted_slow_links

def get_pattern_service(db: Session = Depends(get_db)) -> PatternService:
    return PatternService(db=db)