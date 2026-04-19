"""
routers/auth.py - Endpoint Autentikasi
POST /auth/register - Daftar user baru
POST /auth/login    - Login dan dapatkan JWT token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Autentikasi"])

# Setup password hashing dengan bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password dengan hash yang tersimpan."""
    return pwd_context.verify(plain_password, hashed_password)


# =============================================
# POST /auth/register
# =============================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrasi user baru.
    - Cek apakah email sudah terdaftar
    - Hash password sebelum disimpan
    - Simpan user ke database
    """
    # Cek apakah email sudah ada
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar. Silakan gunakan email lain."
        )
    
    # Validasi role
    if user_data.role not in ["volunteer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role harus 'volunteer' atau 'admin'."
        )
    
    # Hash password & simpan user baru
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# =============================================
# POST /auth/login
# =============================================
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user dan kembalikan JWT token.
    - Cari user berdasarkan email
    - Verifikasi password
    - Generate dan return token JWT
    """
    # Cari user berdasarkan email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah."
        )
    
    # Verifikasi password
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah."
        )
    
    # Buat JWT token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)
    
    return Token(access_token=access_token, token_type="bearer")
