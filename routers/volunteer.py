"""
routers/volunteer.py - CRUD Endpoints untuk Volunteer
POST /volunteers/                   - Protected: User mendaftar ke event
GET  /volunteers/event/{event_id}   - Protected: List relawan per event
GET  /volunteers/my                 - Protected: Riwayat pendaftaran user sendiri
PUT  /volunteers/{id}/status        - Protected (Admin): Update status volunteer
DELETE /volunteers/{id}             - Protected: Batalkan pendaftaran
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.volunteer import Volunteer
from models.event import Event
from schemas.volunteer import VolunteerCreate, VolunteerUpdate, VolunteerResponse
from auth.jwt_handler import get_current_user

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


# =============================================
# POST /volunteers/ - PROTECTED
# =============================================
@router.post("/", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
def register_volunteer(
    volunteer_data: VolunteerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    User mendaftar sebagai relawan untuk suatu event.
    Memerlukan autentikasi JWT.
    Menyimpan: event_id, user_id (dari token), division_choice, motivation_letter.
    """
    # Cek apakah event ada dan masih Open
    event = db.query(Event).filter(Event.id == volunteer_data.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {volunteer_data.event_id} tidak ditemukan."
        )
    
    if event.status != "Open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event ini sudah ditutup untuk pendaftaran relawan."
        )
    
    # Cek apakah user sudah mendaftar ke event ini
    existing = db.query(Volunteer).filter(
        Volunteer.event_id == volunteer_data.event_id,
        Volunteer.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda sudah mendaftar ke event ini sebelumnya."
        )
    
    new_volunteer = Volunteer(
        event_id=volunteer_data.event_id,
        user_id=current_user.id,
        division_choice=volunteer_data.division_choice,
        motivation_letter=volunteer_data.motivation_letter,
        status="Pending"
    )
    
    db.add(new_volunteer)
    db.commit()
    db.refresh(new_volunteer)
    
    return new_volunteer


# =============================================
# GET /volunteers/my - PROTECTED
# =============================================
@router.get("/my", response_model=List[VolunteerResponse], status_code=status.HTTP_200_OK)
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Mendapatkan semua pendaftaran relawan milik user yang sedang login.
    """
    volunteers = db.query(Volunteer).filter(Volunteer.user_id == current_user.id).all()
    return volunteers


# =============================================
# GET /volunteers/event/{event_id} - PROTECTED
# =============================================
@router.get("/event/{event_id}", response_model=List[VolunteerResponse], status_code=status.HTTP_200_OK)
def get_volunteers_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Mendapatkan daftar semua relawan yang mendaftar ke suatu event.
    Memerlukan autentikasi JWT.
    """
    # Cek apakah event ada
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )
    
    volunteers = db.query(Volunteer).filter(Volunteer.event_id == event_id).all()
    return volunteers


# =============================================
# PUT /volunteers/{id}/status - PROTECTED (Admin)
# =============================================
@router.put("/{volunteer_id}/status", response_model=VolunteerResponse, status_code=status.HTTP_200_OK)
def update_volunteer_status(
    volunteer_id: int,
    update_data: VolunteerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Admin dapat mengubah status volunteer: Pending → Accepted / Rejected.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengubah status volunteer."
        )
    
    if update_data.status not in ["Pending", "Accepted", "Rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status harus 'Pending', 'Accepted', atau 'Rejected'."
        )
    
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data volunteer dengan ID {volunteer_id} tidak ditemukan."
        )
    
    volunteer.status = update_data.status
    db.commit()
    db.refresh(volunteer)
    
    return volunteer


# =============================================
# DELETE /volunteers/{id} - PROTECTED
# =============================================
@router.delete("/{volunteer_id}", status_code=status.HTTP_200_OK)
def cancel_volunteer_registration(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Membatalkan pendaftaran relawan.
    User hanya bisa membatalkan pendaftarannya sendiri.
    Admin bisa membatalkan pendaftaran siapa saja.
    """
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data volunteer dengan ID {volunteer_id} tidak ditemukan."
        )
    
    # Cek kepemilikan: user hanya bisa hapus miliknya sendiri (kecuali admin)
    if current_user.role != "admin" and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk membatalkan pendaftaran ini."
        )
    
    db.delete(volunteer)
    db.commit()
    
    return {"message": "Pendaftaran relawan berhasil dibatalkan.", "id": volunteer_id}
