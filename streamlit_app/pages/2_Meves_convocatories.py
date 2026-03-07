import streamlit as st
from sqlalchemy import select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.models import JobPosting, UserPostingStatus
from public_jobs_tracker.ui import get_followed_status, set_followed_status

st.title("Meves convocatories")

posting_id = st.number_input("ID convocatoria", min_value=1, value=1, step=1)
status = st.selectbox("Estat personal", [s.value for s in UserPostingStatus])
notes = st.text_area("Notes")

if st.button("Guardar"):
    with SessionLocal() as session:
        posting = session.scalar(select(JobPosting).where(JobPosting.id == int(posting_id)))
        if not posting:
            st.error("No existeix la convocatoria")
        else:
            set_followed_status(session, posting_id=int(posting_id), status=UserPostingStatus(status), notes=notes)
            st.success("Estat actualitzat")

with SessionLocal() as session:
    followed = get_followed_status(session, int(posting_id))
    if followed:
        st.write({"status": followed.user_status.value, "notes": followed.notes})
