import pytest

from ask_my_docs_api.core.errors import AppError, BadRequestError, ConflictError, NotFoundError


def test_custom_message_overrides_default() -> None:
    exc = NotFoundError("doc 42")
    assert exc.message == "doc 42"


@pytest.mark.parametrize(
    ("error_cls", "expected"),
    [
        (NotFoundError, "Not found"),
        (ConflictError, "Conflict Error"),
        (BadRequestError, "Bad request Error"),
    ],
)
def test_default_message(error_cls: type[AppError], expected: str) -> None:
    exc = error_cls()
    assert exc.message == expected


def test_str_equals_message() -> None:
    assert str(NotFoundError("doc 42")) == "doc 42"
