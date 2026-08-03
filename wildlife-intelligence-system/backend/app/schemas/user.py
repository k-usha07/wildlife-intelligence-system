import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field

ROLE_CHOICES = ("admin", "researcher", "conservation_officer", "forest_department")


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(description=f"One of: {', '.join(ROLE_CHOICES)}")
    organization: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    organization: str | None
    is_active: bool
    created_at: datetime
    role: str

    @classmethod
    def from_orm_with_role(cls, user):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            organization=user.organization,
            is_active=user.is_active,
            created_at=user.created_at,
            role=user.role.name,
        )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class UserRoleUpdate(BaseModel):
    role: str = Field(description=f"One of: {', '.join(ROLE_CHOICES)}")
