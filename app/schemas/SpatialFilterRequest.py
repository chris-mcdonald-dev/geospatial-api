from pydantic import BaseModel, conlist
from typing import List, Optional

class SpatialFilterRequest(BaseModel):
  day: str      
  period: str  
  bbox: conlist(float, min_length=4, max_length=4) # Probably coordinates of the viewport

# TODO: Add response schemas as well if I have time