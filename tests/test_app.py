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


def test_root_redirect(client):
    """Test that the root endpoint redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have activities
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_get_activities_contains_expected_activities(client):
    """Test that the activities list contains expected activities"""
    response = client.get("/activities")
    data = response.json()
    
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club"
    ]
    
    for activity_name in expected_activities:
        assert activity_name in data


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    email = "test@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_signup_for_activity_duplicate(client):
    """Test that signing up twice for the same activity fails"""
    email = "test_duplicate@mergington.edu"
    activity = "Programming Class"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_from_activity_success(client):
    """Test successfully unregistering from an activity"""
    email = "test_unreg@mergington.edu"
    activity = "Art Studio"
    
    # Sign up first
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_unregister_from_activity_not_signed_up(client):
    """Test unregistering from an activity when not signed up"""
    email = "notregistered@mergington.edu"
    activity = "Drama Club"
    
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_signup_and_unregister_flow(client):
    """Test complete signup and unregister flow"""
    email = "flow_test@mergington.edu"
    activity = "Soccer Club"
    
    # Get initial participant count
    response = client.get("/activities")
    initial_participants = len(response.json()[activity]["participants"])
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify participant was added
    response = client.get("/activities")
    new_participants = len(response.json()[activity]["participants"])
    assert new_participants == initial_participants + 1
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    unreg_response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unreg_response.status_code == 200
    
    # Verify participant was removed
    response = client.get("/activities")
    final_participants = len(response.json()[activity]["participants"])
    assert final_participants == initial_participants
    assert email not in response.json()[activity]["participants"]
