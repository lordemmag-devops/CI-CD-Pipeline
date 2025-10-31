"""Test module for Flask CI/CD application."""
"""Tests for Flask CI/CD application."""
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Python CI/CD Demo" in response.data

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert "timestamp" in response.json
    assert "service" in response.json
