import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ask_my_docs_api.api.errors import register_exception_handlers
from ask_my_docs_api.api.main import create_app
from ask_my_docs_api.core.errors import (
    AppError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from ask_my_docs_api.core.middleware import REQUEST_ID_HEADER, RequestIDMiddleware


def make_client(exc: Exception) -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(app)

    @app.get("/raise")
    async def raise_exc() -> None:
        raise exc

    @app.get("/items/{item_id}")
    async def get_item(item_id: int) -> int:
        return item_id

    return TestClient(app, raise_server_exceptions=False)


def test_unhandled_error_hides_details() -> None:
    client = make_client(RuntimeError("secret"))

    response = client.get("/raise")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal"
    assert "secret" not in response.text
    assert REQUEST_ID_HEADER in response.headers


@pytest.mark.parametrize(
    ("exc", "status_code", "code"),
    [
        (UnauthorizedError("x"), 401, "unauthorized"),
        (NotFoundError("x"), 404, "not_found"),
        (BadRequestError("x"), 400, "bad_request"),
        (ConflictError("x"), 409, "conflict"),
        (AppError("x"), 500, "internal"),
    ],
    ids=["unauthorized", "not_found", "bad_request", "conflict", "base_app_error"],
)
def test_app_error_response(exc: AppError, status_code: int, code: str) -> None:
    client = make_client(exc)

    response = client.get("/raise")

    assert response.status_code == status_code
    assert response.json() == {"error": {"code": code, "message": exc.message}}


def test_subclass_inherits_status_from_parent() -> None:
    class DocumentNotFoundError(NotFoundError):
        code = "document_not_found"

    client = make_client(DocumentNotFoundError())

    response = client.get("/raise")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "document_not_found"


def test_unknown_route_returns_not_found() -> None:
    client = make_client(RuntimeError())

    response = client.get("/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_method_not_allowed_keeps_allow_header() -> None:
    client = make_client(RuntimeError())

    response = client.delete("/items/1")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "http_error"
    assert "GET" in response.headers["allow"]


def test_validation_error_returns_details() -> None:
    client = make_client(RuntimeError())

    response = client.get("/items/abc")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["loc"] == ["path", "item_id"]


def test_create_app_registers_handlers() -> None:
    client = TestClient(create_app())

    response = client.get("/nope")

    assert response.json()["error"]["code"] == "not_found"
