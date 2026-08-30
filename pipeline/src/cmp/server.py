"""The local server behind the lens.

    uv run --extra scoring python -m cmp.server

It exists for two reasons a browser cannot cover on its own: it holds the API
key, and it can fetch a URL the viewer names without a cross-origin refusal.
Everything else is cache and refusal.

**It binds to loopback only, and that is not a default to be relaxed.** It holds
a key and will fetch any URL it is handed. It is a tool you run on your own
machine while you look at a document, not a service.

Concurrency lives in the browser. It asks for the reader the viewer chose, then
for the other six in parallel, and each request either returns a reading or an
error naming the reader that failed. There is no job queue and no streaming: with
a threaded server, seven ordinary requests do the same work with none of the
state that a queue would need to keep honest.
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from cmp.ingest import Ingested, ingest as default_ingest
from cmp.lens import LensClient, attend
from cmp.personas import FINANCE_PERSONAS, persona_by_id

__all__ = ["DEFAULT_PORT", "LensService", "make_server", "main"]

DEFAULT_PORT = 8420
ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "pipeline" / ".lenscache"
DIST = ROOT / "viz" / "dist"
FIXTURES = ROOT / "fixtures"

MAX_BODY = 4_000_000


class LensService:
    """Ingest, attend, cache. Every route is a thin wrapper over one of these."""

    def __init__(
        self,
        client: LensClient | None,
        cache_dir: Path = CACHE_DIR,
        ingester: Callable[..., Ingested] = default_ingest,
    ) -> None:
        self.client = client
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._ingest = ingester
        self._lock = threading.Lock()

    # --- documents ---------------------------------------------------------------

    def _doc_path(self, doc_id: str) -> Path:
        # doc_id is our own hex digest, but it arrives over HTTP, so it is never
        # trusted as a path component.
        if not doc_id or not all(c in "0123456789abcdef" for c in doc_id):
            raise KeyError(f"unknown document {doc_id!r}")
        return self.cache_dir / doc_id / "doc.json"

    def ingest(self, url: str | None = None, text: str | None = None) -> dict[str, Any]:
        doc = self._ingest(url=url, text=text) if url else self._ingest(text=text)
        blob = doc.to_dict()
        path = self._doc_path(doc.doc_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(blob))
        return blob

    def document(self, doc_id: str) -> Ingested:
        path = self._doc_path(doc_id)
        if not path.exists():
            raise KeyError(f"unknown document {doc_id!r}; ingest it first")
        raw = json.loads(path.read_text())
        return Ingested(
            doc_id=raw["doc_id"],
            title=raw["title"],
            clauses=raw["clauses"],
            source=raw["source"],
            truncated_from=raw.get("truncated_from"),
        )

    # --- readings ----------------------------------------------------------------

    def attend(self, doc_id: str, persona_id: str) -> dict[str, Any]:
        persona = persona_by_id(persona_id)  # raises KeyError on an unknown reader
        doc = self.document(doc_id)

        cached = self._doc_path(doc_id).parent / f"{persona.id}.json"
        if cached.exists():
            return json.loads(cached.read_text())

        if self.client is None:
            raise RuntimeError(
                "reading live needs an ANTHROPIC_API_KEY; the five documents from "
                "the study are already scored and need no key"
            )

        blob = attend(self.client, persona, doc).to_dict()

        # Written only after a reading validated. A half-parsed field on disk
        # would be served forever as though it were sound.
        with self._lock:
            cached.write_text(json.dumps(blob))
        return blob


def _personas_payload() -> dict[str, Any]:
    return {
        "personas": [
            {
                "id": p.id,
                "label": p.label,
                "mandate": p.mandate,
                "time_horizon": p.time_horizon,
                "loss_function": p.loss_function,
                "reads_for": list(p.reads_for),
                "expert": p.expert,
            }
            for p in FINANCE_PERSONAS
        ]
    }


def make_server(service: LensService, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """A threaded server bound to loopback, wired to one service."""

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt: str, *args: Any) -> None:  # quieter tests
            if os.environ.get("CMP_SERVER_LOG"):
                super().log_message(fmt, *args)

        # --- plumbing ---------------------------------------------------------

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, payload: dict[str, Any]) -> None:
            self._send(status, json.dumps(payload).encode(), "application/json")

        def _error(self, status: int, message: str) -> None:
            self._json(status, {"error": message})

        def _body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                raise ValueError("that document is too large to paste")
            return json.loads(self.rfile.read(length) or b"{}")

        def _file(self, path: Path, content_type: str) -> None:
            if not path.exists():
                self._error(404, f"{path.name} has not been built; run viz/build.py")
                return
            self._send(200, path.read_bytes(), content_type)

        # --- routes -----------------------------------------------------------

        def do_GET(self) -> None:
            route = self.path.split("?")[0]
            if route in ("/", "/lens.html"):
                self._file(DIST / "lens.html", "text/html; charset=utf-8")
            elif route == "/api/personas":
                self._json(200, _personas_payload())
            elif route.startswith("/fixtures/") and route.endswith(".json"):
                name = Path(route).name
                self._file(FIXTURES / name, "application/json")
            else:
                self._error(404, f"no route {route}")

        def do_POST(self) -> None:
            route = self.path.split("?")[0]
            try:
                body = self._body()
            except (ValueError, json.JSONDecodeError) as exc:
                self._error(400, f"that request body was not readable: {exc}")
                return

            if route == "/api/ingest":
                self._ingest_route(body)
            elif route == "/api/attend":
                self._attend_route(body)
            else:
                self._error(404, f"no route {route}")

        def _ingest_route(self, body: dict[str, Any]) -> None:
            url = (body.get("url") or "").strip() or None
            text = body.get("text") or None
            if not url and not text:
                self._error(400, "give a url or some text")
                return
            try:
                self._json(200, service.ingest(url=url, text=text))
            except ValueError as exc:
                self._error(400, str(exc))
            except OSError as exc:
                self._error(502, f"could not read that URL: {exc}")

        def _attend_route(self, body: dict[str, Any]) -> None:
            doc_id = body.get("doc_id") or ""
            persona_id = body.get("persona_id") or ""
            try:
                self._json(200, service.attend(doc_id, persona_id))
            except KeyError as exc:
                self._error(404, str(exc).strip("'\""))
            except RuntimeError as exc:
                # No key is a 503: the page turns this into an offer of the five
                # scored documents rather than an error.
                if "ANTHROPIC_API_KEY" in str(exc):
                    self._error(503, str(exc))
                else:
                    self._error(502, f"{persona_id} could not read it: {exc}")
            except Exception as exc:  # a bad model response, a range violation
                self._error(502, f"{persona_id} could not read it: {exc}")

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def _client_or_none() -> LensClient | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    from cmp.lens import AnthropicLensClient

    return AnthropicLensClient()


def main() -> int:
    port = int(os.environ.get("CMP_PORT", DEFAULT_PORT))
    client = _client_or_none()
    server = make_server(LensService(client=client), port=port)

    print(f"the lens is at http://127.0.0.1:{port}/")
    if client is None:
        print("no ANTHROPIC_API_KEY: live readings are off, the five study "
              "documents still work")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
