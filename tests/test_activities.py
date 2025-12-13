"""Tests for the FastAPI activities endpoints"""
import pytest


class TestActivitiesEndpoints:
    """Test suite for activities endpoints"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify the response contains expected activities
        assert isinstance(data, dict)
        assert "Tennis Club" in data
        assert "Basketball Team" in data
        assert "Drama Club" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        # Check first activity
        activity = data["Tennis Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_signup_new_participant(self, client):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_already_registered(self, client):
        """Test that signing up twice returns an error"""
        # First signup
        client.post("/activities/Tennis%20Club/signup?email=duplicate@mergington.edu")
        
        # Second signup with same email
        response = client.post(
            "/activities/Tennis%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant(self, client):
        """Test unregistering a participant from an activity"""
        # First add a participant
        client.post("/activities/Tennis%20Club/signup?email=tempstudent@mergington.edu")
        
        # Then unregister them
        response = client.post(
            "/activities/Tennis%20Club/unregister?email=tempstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "tempstudent@mergington.edu" in data["message"]

    def test_unregister_not_registered(self, client):
        """Test unregistering a participant who is not registered"""
        response = client.post(
            "/activities/Tennis%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_and_unregister_flow(self, client):
        """Test a complete signup and unregister flow"""
        email = "flow@mergington.edu"
        activity = "Chess%20Club"
        
        # Verify participant is not initially registered
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"]
        assert email not in initial_participants
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify participant is now registered
        response = client.get("/activities")
        registered_participants = response.json()["Chess Club"]["participants"]
        assert email in registered_participants
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant is no longer registered
        response = client.get("/activities")
        final_participants = response.json()["Chess Club"]["participants"]
        assert email not in final_participants
