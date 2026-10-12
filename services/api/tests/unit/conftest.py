from collections.abc import Iterator
from pathlib import Path

import pytest

from ask_my_docs_api.core.config import get_settings


@pytest.fixture(autouse=True)
def clean_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    monkeypatch.chdir(tmp_path)  # в пустой папке .env не найдётся
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/test")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
