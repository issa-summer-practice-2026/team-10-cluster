"""Shared pytest fixtures for the backend."""

import pytest

from app import create_app


@pytest.fixture
def app():
    """A fresh app (and thus a fresh in-memory VehicleState) per test."""
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()
