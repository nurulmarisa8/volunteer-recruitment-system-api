"""
models/user.py - SQLAlchemy Model untuk User (Admin / Pendaftar)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="volunteer")  # "volunteer" atau "admin"

    # Relasi One-to-Many: User memiliki banyak Volunteer registrations
    volunteers = relationship("Volunteer", back_populates="user")
