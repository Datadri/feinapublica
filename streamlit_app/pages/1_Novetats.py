import streamlit as st
from sqlalchemy import select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.models import JobPosting, PostingChangeLog
from public_jobs_tracker.ui import list_recent_changes

st.title("Novetats")

with SessionLocal() as session:
    changes = list_recent_changes(session)
    table = []
    for c in changes:
        posting = session.scalar(select(JobPosting).where(JobPosting.id == c.posting_id))
        table.append(
            {
                "detected_at": c.detected_at,
                "change_type": c.change_type.value,
                "posting_id": c.posting_id,
                "title": posting.title if posting else None,
                "field_name": c.field_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
            }
        )

    st.dataframe(table, use_container_width=True)
