from public_jobs_tracker.utils import compute_hash_content


def test_hash_content_is_stable_for_key_order() -> None:
    a = {"title": "A", "deadline": "2026-03-10", "status": "open"}
    b = {"status": "open", "deadline": "2026-03-10", "title": "A"}

    assert compute_hash_content(a) == compute_hash_content(b)


def test_hash_content_changes_when_material_changes() -> None:
    a = {"title": "A", "deadline": "2026-03-10"}
    b = {"title": "B", "deadline": "2026-03-10"}

    assert compute_hash_content(a) != compute_hash_content(b)
