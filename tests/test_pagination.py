from public_jobs_tracker.sources.cido.client import CidoClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_cido_client_pagination(monkeypatch):
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        offset = int(params["page[offset]"])
        limit = int(params["page[limit]"])
        total = 3
        data = [{"id": str(i), "attributes": {"titol": f"x{i}"}} for i in range(offset, min(offset + limit, total))]
        return DummyResponse({"data": data, "meta": {"total": total}})

    monkeypatch.setattr("public_jobs_tracker.sources.cido.client.httpx.get", fake_get)

    client = CidoClient()
    r1 = client.fetch_page(limit=2, offset=0)
    r2 = client.fetch_page(limit=2, offset=r1.next_offset or 0)

    assert len(r1.records) == 2
    assert r1.next_offset == 2
    assert len(r2.records) == 1
    assert r2.next_offset is None
    assert calls[0]["page[offset]"] == 0
    assert calls[1]["page[offset]"] == 2
