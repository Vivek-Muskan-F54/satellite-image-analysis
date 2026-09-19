import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.deps import get_db
from app.models import Base
from app.core import security
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    assert "id" in data

def test_register_duplicate_email():
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 409

def test_login_user():
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "login@example.com"
    assert "password_hash" not in data["user"]

def test_login_invalid_password():
    client.post(
        "/api/auth/register",
        json={"email": "wrongpass@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "wrongpass@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_get_current_user_me():
    # Register and login
    client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "password": "password123"}
    )
    login_res = client.post(
        "/api/auth/login",
        data={"username": "me@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    # Get me
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    
def test_get_current_user_me_no_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_password_is_hashed():
    client.post(
        "/api/auth/register",
        json={"email": "hash@example.com", "password": "password123"}
    )
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "hash@example.com").first()
    assert user is not None
    assert user.password_hash != "password123"
    assert security.verify_password("password123", user.password_hash)
    db.close()
