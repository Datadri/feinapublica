import streamlit as st
from sqlalchemy import select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.models import JobPosting, PostingChangeLog

st.title("Detall convocatoria")

posting_id = st.number_input("ID convocatoria", min_value=1, value=1, step=1)

with SessionLocal() as session:
    posting = session.scalar(select(JobPosting).where(JobPosting.id == int(posting_id)))
    if posting is None:
        st.warning("No s'ha trobat la convocatoria")
    else:
        st.subheader(posting.title or f"Convocatoria {posting.id}")
        st.write(
            {
                "organization": posting.organization,
                "territory": posting.territory,
                "staff_type": posting.staff_type,
                "status": posting.status,
                "publication_date": posting.publication_date,
                "deadline_date": posting.deadline_date,
                "first_seen_at": posting.first_seen_at,
                "last_seen_at": posting.last_seen_at,
                "last_changed_at": posting.last_changed_at,
                "detail_url": posting.detail_url,
            }
        )

        if posting.detail_url:
            st.link_button("Obrir oferta", posting.detail_url)

        st.markdown("### Historial de canvis")
        logs = session.scalars(select(PostingChangeLog).where(PostingChangeLog.posting_id == posting.id).order_by(PostingChangeLog.detected_at.desc())).all()
        st.dataframe(
            [
                {
                    "detected_at": x.detected_at,
                    "change_type": x.change_type.value,
                    "field_name": x.field_name,
                    "old_value": x.old_value,
                    "new_value": x.new_value,
                    "details": x.details,
                }
                for x in logs
            ],
            use_container_width=True,
        )