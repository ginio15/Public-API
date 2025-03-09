import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from services.db_models import UserDB
from services.security import hash_password
from services.auth_config import decode_access_token

from test.test_main import client, setup_database, override_get_db, test_engine

# Clean the database between tests
@pytest.fixture(autouse=True)
def clean_tables():
    from services.db_models import Base
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# Fixture to create a test user
@pytest.fixture
def create_test_user():
    db = next(override_get_db())
    user = UserDB(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        age=30,
        country="Test Country",
        residence="Test City",
        username="testuser",
        password=hash_password("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login_success(create_test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify the token content
    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert "user_id" in payload

def test_login_invalid_username():
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistentuser",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_invalid_password(create_test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_protected_endpoint_with_token(create_test_user):
    # First login to get the token
    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Use the token to access a protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # verify we got a valid profile back
    assert "username" in response.json()
    assert "email" in response.json()

def test_protected_endpoint_without_token():
    response = client.get("/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
