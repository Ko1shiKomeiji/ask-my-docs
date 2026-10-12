import uuid
from typing import Any

import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ask_my_docs_api.core import middleware
from ask_my_docs_api.core.middleware import REQUEST_ID_HEADER, RequestIDMiddleware


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, Any]:
        return structlog.contextvars.get_contextvars()

    return TestClient(app)


def test_generates_request_id_when_header_is_missing(client: TestClient) -> None:
    response = client.get("/ping")
    request_id = response.headers[REQUEST_ID_HEADER]
    assert str(uuid.UUID(request_id)) == request_id


def test_user_request_id_from_header(client: TestClient) -> None:
    response = client.get("/ping", headers={REQUEST_ID_HEADER: "abc-123"})
    assert response.headers[REQUEST_ID_HEADER] == "abc-123"


@pytest.mark.parametrize("bad_id", ["x" * 65, "a b", "<script>"])
def test_replaces_invalid_request_id(client: TestClient, bad_id: str) -> None:
    response = client.get("/ping", headers={REQUEST_ID_HEADER: bad_id})
    assert response.headers[REQUEST_ID_HEADER] != bad_id


def test_request_id_in_structlog_context(client: TestClient) -> None:
    request_id = str(uuid.uuid4())
    response = client.get("/ping", headers={REQUEST_ID_HEADER: request_id})
    assert response.json()["request_id"] == request_id


def test_request_ids_differ_between_requests(client: TestClient) -> None:
    response1 = client.get("/ping")
    response2 = client.get("/ping")
    assert response1.headers[REQUEST_ID_HEADER] != response2.headers[REQUEST_ID_HEADER]


def test_logs_request_line(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    with structlog.testing.capture_logs() as logs:
        monkeypatch.setattr(middleware, "logger", structlog.get_logger())
        client.get("/ping", headers={REQUEST_ID_HEADER: "abc-123"})

    [entry] = [e for e in logs if e["event"] == "request"]
    assert entry["method"] == "GET"
    assert entry["path"] == "/ping"
    assert entry["status_code"] == 200
    assert entry["duration_ms"] >= 0
