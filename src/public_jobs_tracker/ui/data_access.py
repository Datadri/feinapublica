from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from public_jobs_tracker.config import get_settings
from public_jobs_tracker.models import ChangeType, JobPosting, PostingChangeLog, UserFollowedPosting, UserPostingStatus, UserSavedSearch
from public_jobs_tracker.services import get_or_create_default_user


def get_filters_options(session: Session) -> dict[str, list[str]]:
    def distinct_values(column):
        rows = session.scalars(select(column).where(column.is_not(None)).distinct().order_by(column)).all()
        return [r for r in rows if r]

    return {
        "organization": distinct_values(JobPosting.organization),
        "territory": distinct_values(JobPosting.territory),
        "staff_type": distinct_values(JobPosting.staff_type),
        "status": distinct_values(JobPosting.status),
    }


def list_postings(session: Session, filters: dict, only_followed: bool = False, only_new: bool = False) -> list[JobPosting]:
    stmt = select(JobPosting)

    if only_followed:
        user = get_or_create_default_user(session, get_settings().default_user_email)
        stmt = stmt.join(UserFollowedPosting, UserFollowedPosting.posting_id == JobPosting.id).where(UserFollowedPosting.user_id == user.id)

    if filters.get("text"):
        text = f"%{filters['text']}%"
        stmt = stmt.where(or_(JobPosting.title.ilike(text), JobPosting.summary.ilike(text), JobPosting.organization.ilike(text)))

    for key, column in {
        "organization": JobPosting.organization,
        "territory": JobPosting.territory,
        "staff_type": JobPosting.staff_type,
        "status": JobPosting.status,
    }.items():
        if filters.get(key):
            stmt = stmt.where(column == filters[key])

    if filters.get("deadline_until"):
        stmt = stmt.where(JobPosting.deadline_date <= filters["deadline_until"])

    if only_new:
        days = filters.get("new_days", 7)
        since_dt = datetime.combine(datetime.now(timezone.utc).date() - timedelta(days=days), time.min, tzinfo=timezone.utc)
        stmt = stmt.join(PostingChangeLog, PostingChangeLog.posting_id == JobPosting.id).where(
            PostingChangeLog.change_type == ChangeType.NEW,
            PostingChangeLog.detected_at >= since_dt,
        )

    stmt = stmt.order_by(desc(JobPosting.last_changed_at))
    return session.scalars(stmt).all()


def list_recent_changes(session: Session, limit: int = 200) -> list[PostingChangeLog]:
    stmt = select(PostingChangeLog).order_by(desc(PostingChangeLog.detected_at)).limit(limit)
    return session.scalars(stmt).all()


def get_followed_status(session: Session, posting_id: int) -> UserFollowedPosting | None:
    user = get_or_create_default_user(session, get_settings().default_user_email)
    stmt = select(UserFollowedPosting).where(UserFollowedPosting.user_id == user.id, UserFollowedPosting.posting_id == posting_id)
    return session.scalar(stmt)


def set_followed_status(session: Session, posting_id: int, status: UserPostingStatus, notes: str | None = None) -> None:
    user = get_or_create_default_user(session, get_settings().default_user_email)
    followed = get_followed_status(session, posting_id)
    if followed is None:
        followed = UserFollowedPosting(user_id=user.id, posting_id=posting_id, user_status=status, notes=notes)
        session.add(followed)
    else:
        followed.user_status = status
        followed.notes = notes
    session.commit()


def list_saved_searches(session: Session) -> list[UserSavedSearch]:
    user = get_or_create_default_user(session, get_settings().default_user_email)
    return session.scalars(select(UserSavedSearch).where(UserSavedSearch.user_id == user.id).order_by(desc(UserSavedSearch.created_at))).all()


def create_saved_search(session: Session, name: str, filters_json: dict) -> None:
    user = get_or_create_default_user(session, get_settings().default_user_email)
    session.add(UserSavedSearch(user_id=user.id, name=name, filters_json=filters_json))
    session.commit()
