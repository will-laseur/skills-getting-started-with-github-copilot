from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_root_redirects_to_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_new_student():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "rachel@mergington.edu"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up rachel@mergington.edu for Chess Club"}
    assert "rachel@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_existing_student_returns_400():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "rachel@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_student():
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_student_returns_400():
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notfound@mergington.edu"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_missing_activity_returns_404():
    response = client.delete(
        "/activities/Unknown Activity/unregister",
        params={"email": "rachel@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
