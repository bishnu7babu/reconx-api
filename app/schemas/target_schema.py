from pydantic import BaseModel
from typing import Optional

class TargetSchema(BaseModel):
    host: str
    label: Optional[str] = None