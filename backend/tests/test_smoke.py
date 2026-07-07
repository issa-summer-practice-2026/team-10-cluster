"""Smoke test: the backend package imports cleanly."""


def test_app_package_imports():
    import app

    assert app.__doc__ is not None
