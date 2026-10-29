from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.models import User, Role
from app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse
from app.services.audit_service import create_audit_log
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    role_name = user.role.name if user.role else "Worker"
    access_token = create_access_token(data={"sub": user.email, "role": role_name, "uid": user.id})

    create_audit_log(
        db,
        action="USER_LOGIN",
        entity_type="User",
        entity_id=str(user.id),
        user_id=user.id,
        new_state=f"User {user.email} authenticated successfully with role {role_name}"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": role_name,
            "department": user.department,
            "permissions": user.role.permissions if user.role else []
        }
    }

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    role = db.query(Role).filter(Role.id == user_in.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role_id=user_in.role_id,
        phone=user_in.phone,
        department=user_in.department
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_audit_log(
        db,
        action="USER_REGISTERED",
        entity_type="User",
        entity_id=str(new_user.id),
        user_id=new_user.id,
        new_state=f"New user {new_user.email} registered with role {role.name}"
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role_id=new_user.role_id,
        role_name=role.name,
        is_active=new_user.is_active,
        phone=new_user.phone,
        department=new_user.department,
        created_at=new_user.created_at
    )

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.name if current_user.role else "Worker",
        "department": current_user.department,
        "phone": current_user.phone,
        "permissions": current_user.role.permissions if current_user.role else []
    }

@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password does not match")
    
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    create_audit_log(
        db,
        action="PASSWORD_CHANGED",
        entity_type="User",
        entity_id=str(current_user.id),
        user_id=current_user.id,
        new_state="Password updated securely"
    )

    return {"message": "Password changed successfully"}
