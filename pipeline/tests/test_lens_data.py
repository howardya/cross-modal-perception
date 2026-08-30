"""The payload the lens page is built from."""

from cmp.lens_data import DEFAULT_DOC, DEFAULT_PERSONA, DOCUMENTS, build, persona_payload


def test_all_seven_readers_are_offered():
    assert len(persona_payload()) == 7


def test_every_reader_carries_what_it_is_for():
    for p in persona_payload():
        assert p["mandate"] and p["reads_for"] and p["loss_function"]


def test_exactly_one_reader_is_not_an_expert():
    assert sum(1 for p in persona_payload() if not p["expert"]) == 1


def test_every_document_is_present():
    data = build()
    assert set(data["documents"]) == set(DOCUMENTS)


def test_the_defaults_exist_in_the_payload():
    data = build()
    assert DEFAULT_DOC in data["documents"]
    assert DEFAULT_PERSONA in {p["id"] for p in data["personas"]}


def test_every_reader_has_a_unit_for_every_clause():
    for doc in build()["documents"].values():
        n = len(doc["texts"])
        assert len(doc["fields"]) == 7
        for field in doc["fields"]:
            assert len(field["units"]) == n


def test_reading_order_is_a_real_permutation():
    for doc in build()["documents"].values():
        n = len(doc["texts"])
        for field in doc["fields"]:
            assert sorted(u["order"] for u in field["units"]) == list(range(n))


def test_measured_valence_conflicts_travel_with_the_documents():
    hero = build()["documents"]["meridian-q4"]
    conflicts = [c for c in hero["comparisons"] if c["valence_conflicts"]]
    assert conflicts, "the hero note's expert-versus-lay conflicts are a headline result"


def test_provenance_travels_so_the_page_cannot_show_scores_without_it():
    for doc in build()["documents"].values():
        assert doc["provenance"]["summary"]
