from __future__ import annotations

import asyncio
from types import SimpleNamespace

from app.bot.handlers.superadmin import _is_superadmin


class TestSettings:
    admin_user_ids = {123}


def make_update(user_id: int) -> SimpleNamespace:
    return SimpleNamespace(effective_user=SimpleNamespace(id=user_id))


def test_configured_superadmin_is_allowed(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.bot.handlers.superadmin.get_settings", lambda: TestSettings()
    )
    assert asyncio.run(_is_superadmin(make_update(123), SimpleNamespace())) is True


def test_unconfigured_user_is_denied(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.bot.handlers.superadmin.get_settings", lambda: TestSettings()
    )
    assert asyncio.run(_is_superadmin(make_update(456), SimpleNamespace())) is False


def test_missing_user_is_denied(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.bot.handlers.superadmin.get_settings", lambda: TestSettings()
    )
    update = SimpleNamespace(effective_user=None)
    assert asyncio.run(_is_superadmin(update, SimpleNamespace())) is False
