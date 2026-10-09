from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from ask_my_docs.api.main import create_app


def test_lifespan_creates_engine_and_disposes(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_engine = MagicMock()
    fake_engine.dispose = AsyncMock()
    monkeypatch.setattr("ask_my_docs.api.main.build_engine", lambda settings: fake_engine)

    app = create_app()

    with TestClient(app):
        assert app.state.engine is fake_engine
        fake_engine.dispose.assert_not_awaited()

    fake_engine.dispose.assert_awaited_once()
