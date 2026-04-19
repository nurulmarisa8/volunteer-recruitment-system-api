"""
schemas/volunteer.py - Pydantic Schemas untuk Volunteer
"""

from pydantic import BaseModel
from typing import Optional


class VolunteerCreate(BaseModel):
    event_id: int
    division_choice: str
    motivation_letter: Optional[str] = None


class VolunteerUpdate(BaseModel):
    status: str  # "Pending", "Accepted", "Rejected"


class VolunteerResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    division_choice: str
    motivation_letter: Optional[str]
    status: str

    class Config:
        from_attributes = True
