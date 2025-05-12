from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class SpeedRecord(Base):
    __tablename__ = 'speed_records'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.link_id'))
    date_time = Column(DateTime)

    freeflow = Column(Float) # This is the speed when there is no traffic maybe?
    count = Column(Integer) # Probably the number of vehicles
    std_dev = Column(Float)
    min = Column(Float)
    max = Column(Float)
    confidence = Column(Float) # Seems like a confidence interval should be a float although the data seems to only include ints from what I've seen so far.
    average_speed = Column(Float)
    average_pct_85 = Column(Float) # 85th percentile speed
    average_pct_95 = Column(Float)

    # The mappingss for these are stored in stored in app.constants
    day_of_week = Column(Integer)
    period = Column(Integer)

    link = relationship("Link", back_populates="speed_records")