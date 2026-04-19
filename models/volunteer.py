"""
models/volunteer.py - SQLAlchemy Model untuk Volunteer (Data Relawan per Event)
Relasi: Foreign Key ke Event dan User
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    division_choice = Column(String, nullable=False)  # Contoh: "Acara", "Humas", "Perlengkapan"
    motivation_letter = Column(Text, nullable=True)
    status = Column(String, default="Pending")  # "Pending", "Accepted", "Rejected"

    # Relasi Many-to-One ke Event dan User
    event = relationship("Event", back_populates="volunteers")
    user = relationship("User", back_populates="volunteers")
