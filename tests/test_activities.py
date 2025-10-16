from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

TEST_ACTIVITY = "Test Club"
TEST_EMAIL = "tester@mergington.edu"


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict for each test to avoid cross-test state."""
    # Keep a shallow copy of original activities and restore after test
    original = {k: {**v, "participants": list(v.get("participants", []))} for k, v in activities.items()}
    yield
    activities.clear()
    activities.update({k: {**v, "participants": list(v.get("participants", []))} for k, v in original.items()})


def test_get_activities_returns_dict():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Create a test activity
    activities[TEST_ACTIVITY] = {
        "description": "A temporary test activity",
        "schedule": "Now",
        "max_participants": 5,
        "participants": []
    }

    # Signup
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 200
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]
    assert resp.json()["message"] == f"Signed up {TEST_EMAIL} for {TEST_ACTIVITY}"

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")
    assert resp3.status_code == 200
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]
    assert resp3.json()["message"] == f"Unregistered {TEST_EMAIL} from {TEST_ACTIVITY}"

    # Unregistering again should return 404
    resp4 = client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")
    assert resp4.status_code == 404


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup?email=foo@example.com")
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/NoSuchActivity/unregister?email=foo@example.com")
    assert resp.status_code == 404