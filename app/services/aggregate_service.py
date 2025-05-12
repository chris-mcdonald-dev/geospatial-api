from fastapi import Depends
from app.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app import models
from geoalchemy2.functions import ST_AsGeoJSON, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
import json
from typing import List, Optional, Dict, Any

class AggregateService:
    def __init__(self, db: Session):
        self.db = db

    def get_single_link_aggregate_data(
        self,
        link_id: int,
        target_day_of_week: int,
        target_period: int
    ) -> Optional[Dict[str, Any]]:
        stmt = select(
            models.Link.link_id,
            models.Link.road_name,
            models.Link.length,
            ST_AsGeoJSON(models.Link.geometry).label('geometry'),
            func.avg(models.SpeedRecord.average_speed).label('average_speed')
        ).join(
            models.SpeedRecord, models.Link.link_id == models.SpeedRecord.link_id
        ).where(
            models.Link.link_id == link_id,
            models.SpeedRecord.day_of_week == target_day_of_week,
            models.SpeedRecord.period == target_period
        ).group_by(
            models.Link.link_id,
            models.Link.road_name,
            models.Link.length,
            models.Link.geometry
        )
        result = self.db.execute(stmt).first()

        if result is None:
            return None

        # Format the response
        return {
            "link_id": result.link_id,
            "road_name": result.road_name,
            "average_speed": result.average_speed,
            "length": result.length,
            "geometry": json.loads(result.geometry) if result.geometry else None,
        }

    def get_all_aggregates_data(
        self,
        target_day_of_week: int,
        target_period: int
    ) -> List[Dict[str, Any]]:
        stmt = select(
            models.Link.link_id,
            models.Link.road_name,
            models.Link.length,
            ST_AsGeoJSON(models.Link.geometry).label('geometry'),
            func.avg(models.SpeedRecord.average_speed).label('average_speed')
        ).join(
            models.SpeedRecord, models.Link.link_id == models.SpeedRecord.link_id
        ).where(
            models.SpeedRecord.day_of_week == target_day_of_week,
            models.SpeedRecord.period == target_period
        ).group_by(
            models.Link.link_id,
            models.Link.road_name,
            models.Link.length,
            models.Link.geometry
        )
        results = self.db.execute(stmt).all()

        # Format the response
        formatted_results = []
        for result in results:
            formatted_result = {
                "link_id": result.link_id,
                "road_name": result.road_name,
                "average_speed": result.average_speed,
                "length": result.length,
                "geometry": json.loads(result.geometry) if result.geometry else None,
            }
            formatted_results.append(formatted_result)
        return formatted_results

    def get_spatially_filtered_aggregates_data(
        self,
        target_day_of_week: int,
        target_period: int,
        bbox_coords: List[float] # E.g. [-81.8, 30.1, -81.6, 30.3]. These 4 points draw a box.
    ) -> List[Dict[str, Any]]:
        
        if not isinstance(bbox_coords, list) or len(bbox_coords) != 4:
            raise ValueError("Invalid bbox format. Must be a list of 4 floats [x1, y1, x2, y2]")

        # Set up the bounding box geometry for the PostGIS data
        x1, y1, x2, y2 = bbox_coords
        try:
            bbox_polygon_shape = Polygon([
                (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
            ])
            bbox_geometry = from_shape(bbox_polygon_shape, srid=4326)
        except Exception as e:
            raise ValueError(f"Invalid bbox coordinates: {e}")

        # Query the database for links within the bounding box
        stmt = select(
            models.Link.link_id,
            models.Link.road_name,
            ST_AsGeoJSON(models.Link.geometry).label('geometry'),
            models.Link.length,
            func.avg(models.SpeedRecord.average_speed).label('average_speed')
        ).join(
            models.SpeedRecord, models.Link.link_id == models.SpeedRecord.link_id
        ).where(
            models.Link.geometry.ST_Intersects(bbox_geometry), # Use geoalchemy to check if the link geometry intersects with the bounding box
            models.SpeedRecord.day_of_week == target_day_of_week,
            models.SpeedRecord.period == target_period
        ).group_by(
            models.Link.link_id, models.Link.road_name, models.Link.geometry, models.Link.length
        )
        
        results = self.db.execute(stmt).all()

        # Format the response
        formatted_filtered_links = []
        for result in results:
            filtered_link_dict = {
                "link_id": result.link_id,
                "road_name": result.road_name,
                "geometry": json.loads(result.geometry) if result.geometry else None,
                "length": result.length,
                "average_speed": result.average_speed,
            }
            formatted_filtered_links.append(filtered_link_dict)
        return formatted_filtered_links

def get_aggregate_service(db: Session = Depends(get_db)) -> AggregateService:
    return AggregateService(db=db)