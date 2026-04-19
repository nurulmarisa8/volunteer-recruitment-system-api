"""
schemas/event.py - Pydantic Schemas untuk Event
"""

from pydantic import BaseModel
from typing import Optional


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Open"  # "Open" atau "Closed"


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str

    class Config:
        from_attributes = True
