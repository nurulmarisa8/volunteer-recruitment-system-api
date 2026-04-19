"""
models/event.py - SQLAlchemy Model untuk Event (Kepanitiaan/Program)
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="Open")  # "Open" atau "Closed"

    # Relasi One-to-Many: Event memiliki banyak Volunteer
    volunteers = relationship("Volunteer", back_populates="event", cascade="all, delete-orphan")
