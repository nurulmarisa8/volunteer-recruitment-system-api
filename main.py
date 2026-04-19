"""
main.py - Entry Point FastAPI & CORS Setup
Sistem Rekrutmen Relawan Kampus
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base

# Import semua models agar terbuat saat startup
from models import user, event, volunteer

# Import routers
from routers import auth, event as event_router, volunteer as volunteer_router

# =============================================
# INISIALISASI DATABASE
# =============================================
# Buat semua tabel dari models yang ada
Base.metadata.create_all(bind=engine)

# =============================================
# INISIALISASI APLIKASI FASTAPI
# =============================================
app = FastAPI(
    title="Sistem Rekrutmen Relawan Kampus",
    description="""
    ## API untuk Sistem Rekrutmen Relawan Kampus
    
    Dibangun dengan FastAPI + SQLAlchemy + JWT Authentication
    
    ### Fitur Utama:
    - **Autentikasi JWT**: Register & Login dengan token Bearer
    - **Manajemen Event**: CRUD untuk kepanitiaan/program
    - **Pendaftaran Relawan**: User bisa mendaftar ke event pilihan
    - **Manajemen Status**: Admin bisa approve/reject pendaftaran
    
    ### Cara Menggunakan:
    1. Register akun baru via `POST /auth/register`
    2. Login via `POST /auth/login` untuk mendapatkan token
    3. Klik tombol **Authorize** di atas dan masukkan token
    4. Akses endpoint yang memerlukan autentikasi
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================
# CORS MIDDLEWARE
# =============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Di production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# STATIC FILES (Frontend)
# =============================================
# Mount folder frontend agar bisa diakses
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# =============================================
# INCLUDE ROUTERS
# =============================================
app.include_router(auth.router)
app.include_router(event_router.router)
app.include_router(volunteer_router.router)


# =============================================
# ROOT ENDPOINT
# =============================================
@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - Redirect ke dokumentasi API.
    """
    return {
        "message": "Selamat datang di Sistem Rekrutmen Relawan Kampus API!",
        "docs": "/docs",
        "redoc": "/redoc",
        "frontend": "/static/index.html",
        "version": "1.0.0"
    }


@app.get("/frontend", include_in_schema=False)
def serve_frontend():
    """Serve frontend HTML file."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend tidak ditemukan"}
