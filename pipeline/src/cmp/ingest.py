"""Turn something a viewer pasted into a stimulus the personas can score.

The study's five documents were hand-authored as clause lists, so the pipeline
had no way to read prose it had not been given in pieces. This module is that
missing step, and only that: fetch, reduce to text, split into clauses.

Two limits are deliberate and both are stated to the viewer rather than applied
silently. The **cap** exists because the render stops being legible past roughly
a screen and a half of clauses, and because attention is being modelled as a
finite budget — spreading one budget over three hundred sentences produces a
field that is flat for every reader and therefore says nothing. The **floor**
exists because `salience_quota` is arithmetic over the clause count: below a
handful of clauses the quota permits everything and the readers stop diverging.
"""

from __future__ import annotations

import hashlib
import html
import re
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse

__all__ = [
    "MAX_BYTES",
    "MAX_CLAUSES",
    "MIN_CLAUSES",
    "Ingested",
    "fetch",
    "ingest",
    "strip_html",
    "to_clauses",
]

#: More than this and no reader's attention budget can say anything useful.
MAX_CLAUSES = 120

#: Fewer than this and the salience quota permits everything, so readers stop
#: diverging and the instrument shows a difference that is not there.
MIN_CLAUSES = 6

#: A sentence longer than this is doing more than one thing, and rendering it as
#: a single salience value wastes the distinction.
LONG_CLAUSE = 400

MAX_BYTES = 2_000_000
TIMEOUT = 15
MAX_REDIRECTS = 3
USER_AGENT = "cross-modal-perception/0.1 (local research tool)"

#: Words that end in a period without ending a sentence. Deliberately short:
#: a long list guesses, and the following-word test already catches most cases,
#: since an abbreviation is usually followed by a lowercase word.
_ABBREVIATIONS = {
    "Inc", "Corp", "Ltd", "Co", "plc", "LLC", "Mr", "Mrs", "Ms", "Dr", "Prof",
    "St", "Jr", "Sr", "vs", "etc", "al", "No", "Fig", "Approx", "Est", "Rev",
    "Gen", "Sen", "Rep", "Gov", "Adm", "Capt", "Sept", "Jan", "Feb", "Aug",
    "Oct", "Nov", "Dec",
}

_BLOCK_TAGS = (
    "p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
    "section", "article", "blockquote", "td", "figcaption",
)

_DROPPED_ELEMENTS = ("script", "style", "nav", "header", "footer", "aside", "form",
                     "noscript", "svg", "template", "select", "button")

#: A period, question mark or exclamation, then space, then something that looks
#: like the start of a new sentence.
_SENTENCE_END = re.compile(r"([.?!][\"')\]]?)\s+(?=[A-Z0-9“‘(])")

_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


@dataclass(frozen=True)
class Ingested:
    """A document reduced to the form the scoring prompt expects."""

    doc_id: str
    title: str
    clauses: list[str]
    source: str
    truncated_from: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "clauses": list(self.clauses),
            "source": self.source,
            "truncated_from": self.truncated_from,
        }


def _ends_in_abbreviation(left: str) -> bool:
    """True when the period closing `left` is part of a word, not a sentence."""
    tail = left.rstrip()
    if not tail.endswith("."):
        return False
    word = re.split(r"[\s(\[\"']", tail[:-1])[-1]

    # A single capital letter is an initial: "J. P. Morgan".
    if len(word) == 1 and word.isalpha() and word.isupper():
        return True

    # Dotted acronyms keep their internal periods: "U.S.", "e.g.".
    if "." in word and len(word.replace(".", "")) <= 4:
        return True

    return word in _ABBREVIATIONS


def _split_long(clause: str) -> list[str]:
    """Break a clause that is too long to carry one salience value.

    Only at boundaries an author put there. If there is none, the clause is left
    whole — inventing a break point would mean inventing a unit of attention.
    """
    if len(clause) <= LONG_CLAUSE:
        return [clause]

    for pattern in (r"(?<=;)\s+", r"\s+—\s+", r"\s+--\s+"):
        parts = [p.strip() for p in re.split(pattern, clause) if p.strip()]
        if len(parts) > 1:
            return [q for p in parts for q in _split_long(p)]

    return [clause]


def to_clauses(text: str) -> list[str]:
    """Split prose into the units a persona scores one at a time."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    clauses: list[str] = []
    start = 0
    for match in _SENTENCE_END.finditer(text):
        end = match.end(1)
        candidate = text[start:end]
        if _ends_in_abbreviation(candidate):
            continue
        clauses.append(candidate.strip())
        start = match.end()

    if text[start:].strip():
        clauses.append(text[start:].strip())

    return [c for clause in clauses for c in _split_long(clause)]


def strip_html(source: str, want_title: bool = False) -> str | tuple[str, str]:
    """Reduce a page to the prose a reader would actually read."""
    title = ""
    found = _TITLE.search(source)
    if found:
        title = html.unescape(re.sub(r"<[^>]+>", " ", found.group(1))).strip()

    body = source
    for tag in _DROPPED_ELEMENTS:
        body = re.sub(rf"<{tag}\b.*?</{tag}>", " ", body, flags=re.I | re.S)
        body = re.sub(rf"<{tag}\b[^>]*/?>", " ", body, flags=re.I)

    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    for tag in _BLOCK_TAGS:
        body = re.sub(rf"</?{tag}\b[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)

    kept: list[str] = []
    for line in body.splitlines():
        line = re.sub(r"[ \t\xa0]+", " ", line).strip()
        if not line:
            continue
        # Navigation debris: short, and not a sentence.
        if len(line) < 40 and not re.search(r"[.?!]", line):
            continue
        kept.append(line)

    text = "\n".join(kept)
    return (title, text) if want_title else text


def fetch(url: str) -> tuple[str, str]:
    """Retrieve a URL and reduce it to (title, text).

    Deliberately dumb: no JavaScript is executed, so a page that assembles its
    text in the browser comes back thin. The caller reports that rather than
    pretending the document was short.
    """
    _check_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler,
    )
    with opener.open(request, timeout=TIMEOUT) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"that page is larger than {MAX_BYTES // 1_000_000}MB")

    charset = "utf-8"
    body = raw.decode(charset, errors="replace")

    if "<" in body[:2000] and ">" in body[:2000]:
        title, text = strip_html(body, want_title=True)
    else:
        title, text = "", body
    return title, text


def _check_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"only http and https URLs can be read, not {parsed.scheme or 'that'!r}"
        )
    if not parsed.netloc:
        raise ValueError("that URL has no host")


def _derive_title(clauses: list[str]) -> str:
    first = clauses[0]
    return first if len(first) <= 70 else first[:67].rstrip() + "..."


def ingest(*, url: str | None = None, text: str | None = None) -> Ingested:
    """Fetch or accept a document and reduce it to scorable clauses."""
    if (url is None) == (text is None):
        raise ValueError("give exactly one of url or text")

    if url is not None:
        _check_url(url)
        title, body = fetch(url)
        source = "url"
    else:
        title, body, source = "", text or "", "text"

    clauses = to_clauses(body)
    found = len(clauses)

    if found < MIN_CLAUSES:
        raise ValueError(
            f"that gave {found} clauses; a reading needs at least {MIN_CLAUSES} "
            "for the attention budget to mean anything"
        )

    truncated_from = found if found > MAX_CLAUSES else None
    clauses = clauses[:MAX_CLAUSES]

    digest = hashlib.sha256("\n".join(clauses).encode("utf-8")).hexdigest()[:16]
    return Ingested(
        doc_id=digest,
        title=title.strip() or _derive_title(clauses),
        clauses=clauses,
        source=source,
        truncated_from=truncated_from,
    )
