"""
routers/event.py - CRUD Endpoints untuk Event
GET    /events/       - Publik: List semua event
POST   /events/       - Protected (Admin): Buat event baru
PUT    /events/{id}   - Protected: Update event
DELETE /events/{id}   - Protected (Admin): Hapus event
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.event import Event
from schemas.event import EventCreate, EventUpdate, EventResponse
from auth.jwt_handler import get_current_user, get_admin_user

router = APIRouter(prefix="/events", tags=["Events"])


# =============================================
# GET /events/ - PUBLIK
# =============================================
@router.get("/", response_model=List[EventResponse], status_code=status.HTTP_200_OK)
def get_all_events(db: Session = Depends(get_db)):
    """
    Mendapatkan semua event rekruitmen. Endpoint publik, tidak memerlukan token.
    """
    events = db.query(Event).all()
    return events


# =============================================
# GET /events/{id} - PUBLIK
# =============================================
@router.get("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Mendapatkan detail satu event berdasarkan ID. Endpoint publik.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )
    return event


# =============================================
# POST /events/ - PROTECTED (Admin)
# =============================================
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Membuat event baru. Memerlukan autentikasi JWT.
    Khusus untuk user dengan role admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat membuat event baru."
        )
    
    # Validasi status
    if event_data.status not in ["Open", "Closed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status harus 'Open' atau 'Closed'."
        )
    
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        status=event_data.status
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return new_event


# =============================================
# PUT /events/{id} - PROTECTED
# =============================================
@router.put("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update detail event berdasarkan ID. Memerlukan autentikasi JWT.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )
    
    # Update hanya field yang diberikan (partial update)
    if event_data.title is not None:
        event.title = event_data.title
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.status is not None:
        if event_data.status not in ["Open", "Closed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status harus 'Open' atau 'Closed'."
            )
        event.status = event_data.status
    
    db.commit()
    db.refresh(event)
    
    return event


# =============================================
# DELETE /events/{id} - PROTECTED (Admin)
# =============================================
@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Menghapus event berdasarkan ID. Memerlukan autentikasi JWT admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat menghapus event."
        )
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": f"Event '{event.title}' berhasil dihapus.", "id": event_id}
