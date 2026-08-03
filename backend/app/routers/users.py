from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_roles
from app.core.database import get_db
from app.models.user import Role, User
from app.schemas.user import ROLE_CHOICES, UserOut, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
):
    users = db.query(User).options(joinedload(User.role)).order_by(User.created_at.desc()).all()
    return [UserOut.from_orm_with_role(u) for u in users]


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
):
    if payload.role not in ROLE_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose one of {ROLE_CHOICES}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == payload.role).first()
    user.role_id = role.id
    db.commit()
    db.refresh(user)
    return UserOut.from_orm_with_role(user)


@router.patch("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return UserOut.from_orm_with_role(user)
