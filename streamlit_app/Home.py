import streamlit as st
from sqlalchemy import select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.models import JobPosting
from public_jobs_tracker.ui import get_filters_options, list_postings

st.set_page_config(page_title="Public Jobs Tracker", layout="wide")
st.title("Public Jobs Tracker")

with SessionLocal() as session:
    options = get_filters_options(session)

    col1, col2, col3 = st.columns(3)
    text = col1.text_input("Text lliure")
    organization = col2.selectbox("Ens convocant", [""] + options["organization"])
    territory = col3.selectbox("Territori", [""] + options["territory"])

    col4, col5, col6 = st.columns(3)
    staff_type = col4.selectbox("Tipus de personal", [""] + options["staff_type"])
    status = col5.selectbox("Estat", [""] + options["status"])
    deadline_until = col6.date_input("Data limit fins", value=None)

    col7, col8 = st.columns(2)
    only_new = col7.checkbox("Nomes noves")
    only_followed = col8.checkbox("Nomes seguides")

    filters = {
        "text": text,
        "organization": organization or None,
        "territory": territory or None,
        "staff_type": staff_type or None,
        "status": status or None,
        "deadline_until": deadline_until,
    }

    rows = list_postings(session, filters=filters, only_followed=only_followed, only_new=only_new)

    st.caption(f"Resultats: {len(rows)}")
    table = [
        {
            "id": r.id,
            "title": r.title,
            "organization": r.organization,
            "territory": r.territory,
            "staff_type": r.staff_type,
            "status": r.status,
            "deadline_date": r.deadline_date,
            "last_changed_at": r.last_changed_at,
            "detail_url": r.detail_url,
        }
        for r in rows
    ]
    st.dataframe(
        table,
        use_container_width=True,
        column_config={
            "detail_url": st.column_config.LinkColumn("Enllac oferta", display_text="Obrir"),
        },
    )

    selected_id = st.number_input("ID convocatoria per veure detall", min_value=0, value=0, step=1)
    if selected_id:
        posting = session.scalar(select(JobPosting).where(JobPosting.id == int(selected_id)))
        if posting:
            st.subheader(posting.title or f"Convocatoria {posting.id}")
            st.write(posting.summary or "Sense resum")
            st.write(
                {
                    "organization": posting.organization,
                    "territory": posting.territory,
                    "staff_type": posting.staff_type,
                    "status": posting.status,
                    "deadline_date": posting.deadline_date,
                    "detail_url": posting.detail_url,
                }
            )
            if posting.detail_url:
                st.link_button("Obrir oferta", posting.detail_url)