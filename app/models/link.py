from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db import Base

class Link(Base):
    __tablename__ = 'links'

    link_id = Column(Integer, primary_key=True)
    length = Column(Float)
    road_name = Column(String)
    # 4326 is the standard SRID for GIS data
    geometry = Column(Geometry('MULTILINESTRING', srid=4326, spatial_index=False))
    usdk_speed_category = Column(Integer)
    funclass_id = Column(Integer)
    speedcat = Column(Integer)
    volume_value = Column(Integer)
    volume_bin_id = Column(Integer)
    volumes_bin_description = Column(String)
    # Relationship to SpeedRecord
    speed_records = relationship("SpeedRecord", back_populates="link")