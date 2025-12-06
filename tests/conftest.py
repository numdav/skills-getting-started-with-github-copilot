import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Fixture providing sample activity data"""
    return {
        "name": "Test Club",
        "description": "A test activity",
        "schedule": "Mondays, 3:00 PM - 4:00 PM",
        "max_participants": 10,
        "participants": []
    }
