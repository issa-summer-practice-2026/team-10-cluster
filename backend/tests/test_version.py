"""Unit tests for release-version resolution (`app.version`)."""

from app import version as version_module


def test_env_override_wins(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    assert version_module.get_version() == "1.2.3"


def test_env_override_is_stripped(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "  2.0.0  ")
    assert version_module.get_version() == "2.0.0"


def test_falls_back_to_bundled_version_file(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    # The repo ships backend/VERSION == "0.1.0".
    assert version_module.get_version() == "0.1.0"


def test_default_when_no_env_and_no_file(monkeypatch, tmp_path):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.setattr(version_module, "_VERSION_FILE", tmp_path / "MISSING")
    assert version_module.get_version() == version_module._DEFAULT_VERSION
