import json

import streamlit as st

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.ui import create_saved_search, list_saved_searches

st.title("Cerques guardades")

name = st.text_input("Nom de la cerca")
raw_filters = st.text_area("Filtres JSON", value='{"text": "administratiu"}')

if st.button("Guardar cerca"):
    try:
        filters = json.loads(raw_filters)
        with SessionLocal() as session:
            create_saved_search(session, name=name or "Sense nom", filters_json=filters)
        st.success("Cerca guardada")
    except json.JSONDecodeError:
        st.error("JSON invalid")

with SessionLocal() as session:
    searches = list_saved_searches(session)
    st.dataframe(
        [
            {
                "id": s.id,
                "name": s.name,
                "filters": s.filters_json,
                "created_at": s.created_at,
                "active": s.is_active,
            }
            for s in searches
        ],
        use_container_width=True,
    )
