"""
auth/jwt_handler.py - JWT Token Creation & Verification
Menggunakan python-jose untuk enkripsi token JWT
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db

# =============================================
# KONFIGURASI JWT
# =============================================
SECRET_KEY = "RAHASIA_SANGAT_KUAT_GANTI_DI_PRODUCTION_2024"  # Ganti di production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 jam

# HTTP Bearer scheme untuk Swagger UI
security = HTTPBearer()


# =============================================
# FUNGSI CREATE TOKEN
# =============================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JWT access token.
    
    Args:
        data: Dictionary data yang akan di-encode ke token (biasanya mengandung user_id & email)
        expires_delta: Durasi berlakunya token. Default 24 jam.
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =============================================
# FUNGSI VERIFIKASI TOKEN
# =============================================
def verify_token(token: str) -> dict:
    """
    Memverifikasi JWT token dan mengembalikan payload-nya.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary payload dari token
    
    Raises:
        HTTPException 401 jika token tidak valid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# =============================================
# DEPENDENCY: GET CURRENT USER
# =============================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    FastAPI Dependency untuk mendapatkan user saat ini dari JWT token.
    Digunakan sebagai Depends() di protected endpoints.
    
    Returns:
        User object dari database
    
    Raises:
        HTTPException 401 jika token tidak valid
    """
    from models.user import User  # Import di sini untuk hindari circular import
    
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_admin_user(current_user=Depends(get_current_user)):
    """
    Dependency untuk memastikan user adalah admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat melakukan operasi ini."
        )
    return current_user
