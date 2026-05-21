import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_already_signed():
    email = activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 400


def test_signup_unknown_activity():
    resp = client.post(f"/activities/Unknown/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_success():
    email = "toremove@mergington.edu"
    # First sign up
    client.post(f"/activities/Programming Class/signup", params={"email": email})
    assert email in activities["Programming Class"]["participants"]
    # Then unregister
    resp = client.post(f"/activities/Programming Class/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Programming Class"]["participants"]


def test_unregister_not_signed():
    resp = client.post(f"/activities/Gym Class/unregister", params={"email": "nosuch@mergington.edu"})
    assert resp.status_code == 400


def test_unregister_unknown_activity():
    resp = client.post(f"/activities/Unknown/unregister", params={"email": "a@b.com"})
    assert resp.status_code == 404
