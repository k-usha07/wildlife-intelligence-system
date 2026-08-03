"""Seed roles and a demo admin user.

Run with:  python -m app.core.seed
"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import Role, User

ROLES = [
    ("admin", "Full platform administration"),
    ("researcher", "Wildlife Researcher"),
    ("conservation_officer", "Conservation Officer"),
    ("forest_department", "Forest Department Officer"),
]

DEMO_ADMIN = {
    "full_name": "Platform Admin",
    "email": "admin@wildlife.org",
    "password": "ChangeMe123!",
    "organization": "Wildlife Intelligence Platform",
}


def seed():
    db = SessionLocal()
    try:
        for name, description in ROLES:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name, description=description))
        db.commit()

        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not db.query(User).filter(User.email == DEMO_ADMIN["email"]).first():
            db.add(
                User(
                    full_name=DEMO_ADMIN["full_name"],
                    email=DEMO_ADMIN["email"],
                    hashed_password=hash_password(DEMO_ADMIN["password"]),
                    role_id=admin_role.id,
                    organization=DEMO_ADMIN["organization"],
                )
            )
            db.commit()
            print(f"Seeded demo admin: {DEMO_ADMIN['email']} / {DEMO_ADMIN['password']}")
        else:
            print("Demo admin already exists, skipping.")

        print("Roles seeded:", [r for r, _ in ROLES])
    finally:
        db.close()


if __name__ == "__main__":
    seed()
