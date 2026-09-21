import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.models.user import User
from app.models.image import SatelliteImage
from app.core import security
import os
import shutil
import io
from PIL import Image

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_images.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()



client = TestClient(app)

# Helper to create a valid dummy image in memory
def create_test_image(format="JPEG", size=(100, 100)):
    file = io.BytesIO()
    image = Image.new("RGB", size, color="red")
    image.save(file, format=format)
    file.seek(0)
    return file

@pytest.fixture(autouse=True)
def setup_db_and_storage():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    os.environ["STORAGE_LOCAL_ROOT"] = "test_storage/uploads"
    os.environ["STORAGE_PROVIDER"] = "local"
    from app.core.config import settings
    settings.STORAGE_LOCAL_ROOT = "test_storage/uploads"
    settings.STORAGE_PROVIDER = "local"
    
    from app.storage import storage_service
    # Re-initialize local storage service with test path if needed
    if hasattr(storage_service, "base_dir"):
        storage_service.base_dir = "test_storage/uploads"
        os.makedirs("test_storage/uploads", exist_ok=True)
        
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    app.dependency_overrides.clear()

@pytest.fixture
def auth_token():
    db = TestingSessionLocal()
    user = User(email="testimage@example.com", password_hash=security.get_password_hash("password123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = security.create_access_token(user.id)
    db.close()
    return {"Authorization": f"Bearer {token}", "user_id": user.id}

@pytest.fixture
def auth_token_user_b():
    db = TestingSessionLocal()
    user = User(email="userb@example.com", password_hash=security.get_password_hash("password123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = security.create_access_token(user.id)
    db.close()
    return {"Authorization": f"Bearer {token}", "user_id": user.id}

def test_upload_valid_image(auth_token):
    img_bytes = create_test_image("JPEG")
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test.jpg"
    assert data["mime_type"] == "image/jpeg"
    assert data["width"] == 100
    assert data["height"] == 100
    assert "id" in data
    
    # Verify DB
    db = TestingSessionLocal()
    img_db = db.query(SatelliteImage).filter(SatelliteImage.id == data["id"]).first()
    assert img_db is not None
    assert img_db.user_id == auth_token["user_id"]
    db.close()

def test_upload_unauthenticated():
    img_bytes = create_test_image("JPEG")
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/api/images/upload", files=files)
    assert response.status_code == 401

def test_upload_invalid_extension(auth_token):
    img_bytes = create_test_image("JPEG")
    files = {"file": ("test.txt", img_bytes, "text/plain")}
    response = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    assert response.status_code == 400

def test_upload_malformed_image(auth_token):
    files = {"file": ("test.jpg", b"not an image", "image/jpeg")}
    response = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    assert response.status_code == 400
    assert "Invalid or malformed image" in response.json()["detail"]

def test_list_and_get_images(auth_token):
    # Upload one
    img_bytes = create_test_image("PNG")
    files = {"file": ("test.png", img_bytes, "image/png")}
    upload_res = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    img_id = upload_res.json()["id"]
    
    # List
    list_res = client.get("/api/images", headers={"Authorization": auth_token["Authorization"]})
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == img_id
    
    # Get details
    get_res = client.get(f"/api/images/{img_id}", headers={"Authorization": auth_token["Authorization"]})
    assert get_res.status_code == 200
    assert get_res.json()["id"] == img_id

def test_cross_user_access(auth_token, auth_token_user_b):
    # User A uploads
    img_bytes = create_test_image("JPEG")
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    upload_res = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    img_id = upload_res.json()["id"]
    
    # User B tries to get it
    get_res = client.get(f"/api/images/{img_id}", headers={"Authorization": auth_token_user_b["Authorization"]})
    assert get_res.status_code == 404
    
    # User B tries to delete it
    del_res = client.delete(f"/api/images/{img_id}", headers={"Authorization": auth_token_user_b["Authorization"]})
    assert del_res.status_code == 404

def test_delete_image(auth_token):
    # Upload
    img_bytes = create_test_image("JPEG")
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    upload_res = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files=files
    )
    img_id = upload_res.json()["id"]
    
    # Verify file exists
    db = TestingSessionLocal()
    img_db = db.query(SatelliteImage).filter(SatelliteImage.id == img_id).first()
    storage_key = img_db.storage_key
    
    from app.storage import storage_service
    assert storage_service.exists(storage_key)
    db.close()
    
    # Delete
    del_res = client.delete(f"/api/images/{img_id}", headers={"Authorization": auth_token["Authorization"]})
    assert del_res.status_code == 200
    
    # Verify file deleted
    assert not storage_service.exists(storage_key)
    
    # Verify DB deleted
    db = TestingSessionLocal()
    img_db_after = db.query(SatelliteImage).filter(SatelliteImage.id == img_id).first()
    assert img_db_after is None
    db.close()
