from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, func, or_, select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.models import JobPosting, PostingChangeLog, User, UserFollowedPosting, UserPostingStatus, UserSavedSearch


class PostingOut(BaseModel):
    id: int
    source_record_id: str

    # Existing normalized fields
    title: str | None
    organization: str | None
    territory: str | None
    staff_type: str | None
    status: str | None
    publication_date: date | None
    deadline_date: date | None
    detail_url: str | None
    summary: str | None

    # Requested explicit CIDO fields
    institucio_desenvolupat: str | None
    ambit: str | None
    titol: str | None
    num_places: int | None
    tipus_personal: str | None
    grup_titulacio: str | None
    sistema_seleccio: str | None
    data_finalitzacio: date | None
    estat: str | None
    expedient: str | None
    url_web: str | None

    last_changed_at: str | None


class ChangeOut(BaseModel):
    id: int
    posting_id: int
    change_type: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    detected_at: str | None


class SavedSearchOut(BaseModel):
    id: int
    name: str
    filters_json: dict
    is_active: bool


app = FastAPI(title="Public Jobs Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/postings")
def list_postings(
    q: str | None = None,
    organization: str | None = None,
    territory: str | None = None,
    staff_type: str | None = None,
    status: str | None = None,
    min_publication_date: date | None = None,
    only_followed: bool = False,
    user_email: str = "demo@public-jobs-tracker.local",
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    with SessionLocal() as session:
        stmt = select(JobPosting)

        if only_followed:
            user = session.scalar(select(User).where(User.email == user_email))
            if user is None:
                return {"items": [], "total": 0}
            stmt = stmt.join(UserFollowedPosting, UserFollowedPosting.posting_id == JobPosting.id).where(UserFollowedPosting.user_id == user.id)

        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(JobPosting.title.ilike(like), JobPosting.summary.ilike(like), JobPosting.organization.ilike(like)))

        if organization:
            stmt = stmt.where(JobPosting.organization == organization)
        if territory:
            stmt = stmt.where(JobPosting.territory == territory)
        if staff_type:
            stmt = stmt.where(JobPosting.staff_type == staff_type)
        if status:
            stmt = stmt.where(JobPosting.status == status)
        if min_publication_date:
            stmt = stmt.where(JobPosting.publication_date >= min_publication_date)

        total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = session.scalars(stmt.order_by(desc(JobPosting.last_changed_at)).offset(offset).limit(limit)).all()

        items = [
            PostingOut(
                id=row.id,
                source_record_id=row.source_record_id,
                title=row.title,
                organization=row.organization,
                territory=row.territory,
                staff_type=row.staff_type,
                status=row.status,
                publication_date=row.publication_date,
                deadline_date=row.deadline_date,
                detail_url=row.detail_url,
                summary=row.summary,
                institucio_desenvolupat=row.institucio_desenvolupat,
                ambit=row.ambit,
                titol=row.titol,
                num_places=row.num_places,
                tipus_personal=row.tipus_personal,
                grup_titulacio=row.grup_titulacio,
                sistema_seleccio=row.sistema_seleccio,
                data_finalitzacio=row.data_finalitzacio,
                estat=row.estat,
                expedient=row.expedient,
                url_web=row.url_web,
                last_changed_at=row.last_changed_at.isoformat() if row.last_changed_at else None,
            ).model_dump()
            for row in rows
        ]
        return {"items": items, "total": total}


@app.get("/api/postings/{posting_id}")
def get_posting(posting_id: int) -> dict:
    with SessionLocal() as session:
        posting = session.get(JobPosting, posting_id)
        if posting is None:
            return {"item": None, "changes": []}

        changes = session.scalars(
            select(PostingChangeLog).where(PostingChangeLog.posting_id == posting_id).order_by(desc(PostingChangeLog.detected_at)).limit(200)
        ).all()

        item = PostingOut(
            id=posting.id,
            source_record_id=posting.source_record_id,
            title=posting.title,
            organization=posting.organization,
            territory=posting.territory,
            staff_type=posting.staff_type,
            status=posting.status,
            publication_date=posting.publication_date,
            deadline_date=posting.deadline_date,
            detail_url=posting.detail_url,
            summary=posting.summary,
            institucio_desenvolupat=posting.institucio_desenvolupat,
            ambit=posting.ambit,
            titol=posting.titol,
            num_places=posting.num_places,
            tipus_personal=posting.tipus_personal,
            grup_titulacio=posting.grup_titulacio,
            sistema_seleccio=posting.sistema_seleccio,
            data_finalitzacio=posting.data_finalitzacio,
            estat=posting.estat,
            expedient=posting.expedient,
            url_web=posting.url_web,
            last_changed_at=posting.last_changed_at.isoformat() if posting.last_changed_at else None,
        ).model_dump()

        change_items = [
            ChangeOut(
                id=chg.id,
                posting_id=chg.posting_id,
                change_type=chg.change_type.value,
                field_name=chg.field_name,
                old_value=chg.old_value,
                new_value=chg.new_value,
                detected_at=chg.detected_at.isoformat() if chg.detected_at else None,
            ).model_dump()
            for chg in changes
        ]

        return {"item": item, "changes": change_items}


@app.get("/api/changes/recent")
def recent_changes(limit: int = Query(default=200, ge=1, le=1000)) -> list[dict]:
    with SessionLocal() as session:
        rows = session.scalars(select(PostingChangeLog).order_by(desc(PostingChangeLog.detected_at)).limit(limit)).all()
        return [
            ChangeOut(
                id=row.id,
                posting_id=row.posting_id,
                change_type=row.change_type.value,
                field_name=row.field_name,
                old_value=row.old_value,
                new_value=row.new_value,
                detected_at=row.detected_at.isoformat() if row.detected_at else None,
            ).model_dump()
            for row in rows
        ]


@app.get("/api/saved-searches")
def list_saved_searches(user_email: str = "demo@public-jobs-tracker.local") -> list[dict]:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == user_email))
        if user is None:
            return []
        rows = session.scalars(select(UserSavedSearch).where(UserSavedSearch.user_id == user.id).order_by(desc(UserSavedSearch.created_at))).all()
        return [SavedSearchOut(id=r.id, name=r.name, filters_json=r.filters_json, is_active=r.is_active).model_dump() for r in rows]


@app.get("/api/followed")
def list_followed(user_email: str = "demo@public-jobs-tracker.local") -> list[dict]:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == user_email))
        if user is None:
            return []
        rows = session.scalars(select(UserFollowedPosting).where(UserFollowedPosting.user_id == user.id)).all()
        return [{"posting_id": r.posting_id, "user_status": r.user_status.value, "notes": r.notes} for r in rows]


@app.get("/api/options")
def filter_options() -> dict:
    with SessionLocal() as session:
        def get_distinct(column):
            return [x for x in session.scalars(select(column).where(column.is_not(None)).distinct().order_by(column)).all() if x]

        return {
            "organization": get_distinct(JobPosting.organization),
            "territory": get_distinct(JobPosting.territory),
            "staff_type": get_distinct(JobPosting.staff_type),
            "status": get_distinct(JobPosting.status),
            "user_status": [s.value for s in UserPostingStatus],
        }
