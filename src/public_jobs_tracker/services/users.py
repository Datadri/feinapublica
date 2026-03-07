from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from public_jobs_tracker.models import User


def get_or_create_default_user(session: Session, email: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(email=email, display_name="Demo User")
    session.add(user)
    session.flush()
    return user
