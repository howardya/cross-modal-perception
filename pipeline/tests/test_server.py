"""The local server behind the lens.

It exists to hold the API key and to do the two things a browser cannot: fetch a
URL cross-origin, and talk to the Anthropic API. Everything it does is either
cached or refused, and these tests pin which is which — particularly the paths
where it has no key, because degrading to the study's five documents rather than
to an error is a design commitment, not a fallback.
"""

import json
import threading
import urllib.error
import urllib.request

import pytest

from cmp.ingest import Ingested
from cmp.server import LensService, make_server

SIX = " ".join(f"Sentence number {i} says something real." for i in range(6))


def payload(n=6, notes=None):
    units = []
    for i in range(n):
        unit = {
            "salience": round(0.1 + 0.1 * i, 2),
            "valence": 0.2,
            "chunk": i // 2,
            "arousal": 0.3,
        }
        if notes and i in notes:
            unit["note"] = notes[i]
        units.append(unit)
    return {"units": units}


class StubClient:
    def __init__(self, response=None, fail=False):
        self.response = response if response is not None else payload()
        self.fail = fail
        self.calls = []

    def raw_attend(self, persona, stimulus):
        self.calls.append(persona.id)
        if self.fail:
            raise RuntimeError("the model was unreachable")
        return self.response


@pytest.fixture
def service(tmp_path):
    return LensService(client=StubClient(), cache_dir=tmp_path)


@pytest.fixture
def live(service):
    server = make_server(service, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def post(base, path, body):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, json.loads(response.read())


def get(base, path):
    with urllib.request.urlopen(base + path, timeout=5) as response:
        return response.status, response.read()


# --- the service ---------------------------------------------------------------------


def test_ingesting_text_returns_its_clauses(service):
    got = service.ingest(text=SIX)
    assert len(got["clauses"]) == 6
    assert got["doc_id"]


def test_attending_returns_a_field_over_every_clause(service):
    doc = service.ingest(text=SIX)
    field = service.attend(doc["doc_id"], "credit-analyst")
    assert len(field["units"]) == 6
    assert field["persona_id"] == "credit-analyst"


def test_every_live_reading_declares_one_sample(service):
    doc = service.ingest(text=SIX)
    field = service.attend(doc["doc_id"], "credit-analyst")
    assert field["samples"] == 1
    assert field["reliability_measured"] is False


def test_a_second_attend_is_served_from_cache_without_calling_the_model(service):
    doc = service.ingest(text=SIX)
    service.attend(doc["doc_id"], "credit-analyst")
    service.attend(doc["doc_id"], "credit-analyst")
    assert service.client.calls == ["credit-analyst"]


def test_the_cache_survives_a_new_service_over_the_same_directory(tmp_path):
    first = LensService(client=StubClient(), cache_dir=tmp_path)
    doc = first.ingest(text=SIX)
    first.attend(doc["doc_id"], "credit-analyst")

    second = LensService(client=StubClient(), cache_dir=tmp_path)
    second.attend(doc["doc_id"], "credit-analyst")
    assert second.client.calls == []


def test_different_personas_are_cached_separately(service):
    doc = service.ingest(text=SIX)
    service.attend(doc["doc_id"], "credit-analyst")
    service.attend(doc["doc_id"], "short-seller")
    assert service.client.calls == ["credit-analyst", "short-seller"]


def test_an_unknown_document_is_refused(service):
    with pytest.raises(KeyError):
        service.attend("nosuchdoc", "credit-analyst")


def test_an_unknown_persona_is_refused(service):
    doc = service.ingest(text=SIX)
    with pytest.raises(KeyError):
        service.attend(doc["doc_id"], "astrologer")


def test_a_document_that_is_too_short_is_refused(service):
    with pytest.raises(ValueError):
        service.ingest(text="Revenue rose. Margin fell.")


def test_without_a_client_attending_is_refused_but_ingesting_is_not(tmp_path):
    offline = LensService(client=None, cache_dir=tmp_path)
    doc = offline.ingest(text=SIX)
    assert len(doc["clauses"]) == 6
    with pytest.raises(RuntimeError, match="key"):
        offline.attend(doc["doc_id"], "credit-analyst")


def test_a_failed_reading_is_not_cached(service):
    doc = service.ingest(text=SIX)
    service.client.fail = True
    with pytest.raises(RuntimeError):
        service.attend(doc["doc_id"], "credit-analyst")
    service.client.fail = False
    field = service.attend(doc["doc_id"], "credit-analyst")
    assert len(field["units"]) == 6


def test_a_url_ingest_uses_the_injected_fetcher(tmp_path):
    def fake(*, url=None, text=None):
        assert url == "https://example.com/q4"
        return Ingested(doc_id="facade", title="Q4", clauses=[SIX] * 6, source="url")

    service = LensService(client=StubClient(), cache_dir=tmp_path, ingester=fake)
    assert service.ingest(url="https://example.com/q4")["title"] == "Q4"


# --- the routes ----------------------------------------------------------------------


def test_the_personas_route_lists_all_seven(live):
    status, body = get(live, "/api/personas")
    assert status == 200
    assert len(json.loads(body)["personas"]) == 7


def test_the_personas_route_carries_what_each_reader_reads_for(live):
    _, body = get(live, "/api/personas")
    first = json.loads(body)["personas"][0]
    assert first["reads_for"] and first["mandate"] and first["label"]


def test_posting_text_returns_clauses(live):
    status, body = post(live, "/api/ingest", {"text": SIX})
    assert status == 200
    assert len(body["clauses"]) == 6


def test_posting_then_attending_returns_a_field(live):
    _, doc = post(live, "/api/ingest", {"text": SIX})
    status, field = post(live, "/api/attend",
                         {"doc_id": doc["doc_id"], "persona_id": "risk-officer"})
    assert status == 200
    assert field["persona_id"] == "risk-officer"


def test_a_short_document_comes_back_as_400_with_a_reason(live):
    with pytest.raises(urllib.error.HTTPError) as caught:
        post(live, "/api/ingest", {"text": "Revenue rose. Margin fell."})
    assert caught.value.code == 400
    assert "at least" in json.loads(caught.value.read())["error"]


def test_an_unknown_document_comes_back_as_404(live):
    with pytest.raises(urllib.error.HTTPError) as caught:
        post(live, "/api/attend", {"doc_id": "nope", "persona_id": "risk-officer"})
    assert caught.value.code == 404


def test_a_scoring_failure_comes_back_as_502_naming_the_persona(live, service):
    _, doc = post(live, "/api/ingest", {"text": SIX})
    service.client.fail = True
    with pytest.raises(urllib.error.HTTPError) as caught:
        post(live, "/api/attend",
             {"doc_id": doc["doc_id"], "persona_id": "short-seller"})
    assert caught.value.code == 502
    assert "short-seller" in json.loads(caught.value.read())["error"]


def test_no_key_comes_back_as_503_so_the_page_can_offer_the_study_documents(tmp_path):
    offline = LensService(client=None, cache_dir=tmp_path)
    server = make_server(offline, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        _, doc = post(base, "/api/ingest", {"text": SIX})
        with pytest.raises(urllib.error.HTTPError) as caught:
            post(base, "/api/attend",
                 {"doc_id": doc["doc_id"], "persona_id": "risk-officer"})
        assert caught.value.code == 503
    finally:
        server.shutdown()
        server.server_close()


def test_an_unknown_route_is_404(live):
    with pytest.raises(urllib.error.HTTPError) as caught:
        get(live, "/api/nothing")
    assert caught.value.code == 404


def test_malformed_json_is_400_not_a_traceback(live):
    request = urllib.request.Request(
        live + "/api/ingest", data=b"{not json", method="POST",
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(urllib.error.HTTPError) as caught:
        urllib.request.urlopen(request, timeout=5)
    assert caught.value.code == 400


def test_the_server_binds_to_loopback_only(service):
    server = make_server(service, port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_a_document_id_is_never_trusted_as_a_path(service):
    for hostile in ("../../etc/passwd", "..", "a/b", "AAAA"):
        with pytest.raises(KeyError):
            service.attend(hostile, "credit-analyst")
