"""Turning something a viewer pasted into a stimulus the personas can score.

The study's five documents were hand-authored as clause lists. Nothing here
existed for arbitrary prose, so these tests pin the two decisions that matter:
where a clause ends, and when a document is refused rather than rendered badly.
"""

import pytest

from cmp.ingest import (
    MAX_CLAUSES,
    MIN_CLAUSES,
    Ingested,
    ingest,
    strip_html,
    to_clauses,
)


# --- clause splitting ---------------------------------------------------------------


def test_splits_on_sentence_endings():
    assert to_clauses("Revenue rose. Margin fell. Debt grew.") == [
        "Revenue rose.",
        "Margin fell.",
        "Debt grew.",
    ]


def test_splits_on_question_and_exclamation():
    assert len(to_clauses("Is it cash? It is not! We checked.")) == 3


def test_does_not_split_inside_a_company_abbreviation():
    text = "Acme Inc. reported a loss. Beta Corp. did not."
    assert to_clauses(text) == ["Acme Inc. reported a loss.", "Beta Corp. did not."]


def test_does_not_split_after_a_single_initial():
    assert to_clauses("J. P. Morgan advised on it. The fee was $4m.") == [
        "J. P. Morgan advised on it.",
        "The fee was $4m.",
    ]


def test_does_not_split_inside_us_or_a_quarter_label():
    text = "U.S. volumes fell in Q4. 2026 guidance was withheld."
    assert to_clauses(text)[0] == "U.S. volumes fell in Q4."


def test_a_decimal_number_is_not_a_sentence_end():
    assert to_clauses("Leverage reached 4.1 turns. That breaches the test.") == [
        "Leverage reached 4.1 turns.",
        "That breaches the test.",
    ]


def test_a_very_long_sentence_is_split_further_at_semicolons():
    long = (
        "The company said that " + "revenue grew and costs also grew " * 12
        + "; the auditors disagreed with that characterisation entirely."
    )
    parts = to_clauses(long)
    assert len(parts) == 2
    assert parts[1].startswith("the auditors")


def test_a_long_sentence_with_no_break_point_is_left_whole():
    long = "x" * 500 + "."
    assert to_clauses(long) == [long]


def test_whitespace_and_blank_lines_collapse():
    assert to_clauses("Revenue rose.\n\n\n   Margin  fell.") == [
        "Revenue rose.",
        "Margin fell.",
    ]


def test_trailing_fragment_without_punctuation_is_kept():
    assert to_clauses("Revenue rose. Margin fell")[-1] == "Margin fell"


# --- html ---------------------------------------------------------------------------


def test_strip_html_removes_script_and_style_content():
    html = "<p>Revenue rose.</p><script>var x = 'Margin fell.';</script>"
    out = strip_html(html)
    assert "Revenue rose." in out
    assert "Margin fell." not in out


def test_strip_html_removes_navigation_furniture():
    html = "<nav>Home About Contact</nav><p>Revenue rose sharply this quarter.</p>"
    out = strip_html(html)
    assert "About" not in out
    assert "Revenue rose sharply" in out


def test_strip_html_drops_short_lines_with_no_sentence_punctuation():
    html = "<div>Sign in</div><p>Revenue rose nineteen percent this quarter.</p>"
    out = strip_html(html)
    assert "Sign in" not in out


def test_strip_html_decodes_entities():
    assert "AT&T" in strip_html("<p>AT&amp;T raised its dividend this quarter.</p>")


def test_strip_html_finds_the_title():
    html = "<html><head><title>Q4 results</title></head><body><p>A. B. C. D. E. F.</p></body></html>"
    assert "Q4 results" in strip_html(html, want_title=True)[0]


# --- ingest -------------------------------------------------------------------------


SIX = " ".join(f"Sentence number {i} says something." for i in range(6))


def test_ingest_text_returns_clauses_and_a_content_hash():
    got = ingest(text=SIX)
    assert isinstance(got, Ingested)
    assert len(got.clauses) == 6
    assert len(got.doc_id) == 16
    assert got.source == "text"


def test_the_same_text_ingests_to_the_same_doc_id():
    assert ingest(text=SIX).doc_id == ingest(text=SIX + "   ").doc_id


def test_different_text_ingests_to_a_different_doc_id():
    assert ingest(text=SIX).doc_id != ingest(text=SIX + " And one more thing.").doc_id


def test_a_document_over_the_cap_is_truncated_and_says_so():
    many = " ".join(f"Sentence number {i} says something." for i in range(MAX_CLAUSES + 40))
    got = ingest(text=many)
    assert len(got.clauses) == MAX_CLAUSES
    assert got.truncated_from == MAX_CLAUSES + 40


def test_a_document_within_the_cap_reports_no_truncation():
    assert ingest(text=SIX).truncated_from is None


def test_too_few_clauses_is_refused_rather_than_rendered():
    with pytest.raises(ValueError, match="at least"):
        ingest(text="Revenue rose. Margin fell.")


def test_the_refusal_names_how_many_clauses_were_found():
    with pytest.raises(ValueError, match="2"):
        ingest(text="Revenue rose. Margin fell.")


def test_min_clauses_is_above_the_salience_quota_floor():
    # salience_quota refuses fewer than two; the quota is meaningless well above that.
    assert MIN_CLAUSES >= 6


def test_ingest_needs_either_a_url_or_text():
    with pytest.raises(ValueError):
        ingest()


def test_ingest_refuses_both_at_once():
    with pytest.raises(ValueError):
        ingest(url="https://example.com", text=SIX)


def test_a_title_is_derived_when_none_is_given():
    assert ingest(text=SIX).title


# --- url safety ---------------------------------------------------------------------


@pytest.mark.parametrize("url", ["file:///etc/passwd", "javascript:alert(1)", "ftp://x/y"])
def test_only_http_urls_are_fetched(url):
    with pytest.raises(ValueError, match="http"):
        ingest(url=url)


def test_a_url_without_a_host_is_refused():
    with pytest.raises(ValueError):
        ingest(url="http:///nowhere")
