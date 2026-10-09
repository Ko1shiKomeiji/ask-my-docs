from pydantic import ValidationError
from pytest import MonkeyPatch, mark, raises

from ask_my_docs.core.config import get_settings


@mark.parametrize("raw", ["local", "LOCAL", "Local"])
def test_config_env_field_case_insensitive(raw: str, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", raw)
    assert get_settings().env == "local"


@mark.parametrize("raw", ["info", "INFO", "INFO"])
def test_config_log_level_field_case_insensitive(raw: str, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", raw)
    assert get_settings().log_level == "INFO"


def test_app_stops_with_invalid_config_params(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "bebra")
    with raises(ValidationError):
        get_settings()
