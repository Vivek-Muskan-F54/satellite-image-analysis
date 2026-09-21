import pytest
from fastapi.testclient import TestClient
import io
import os
import shutil
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.models.image import SatelliteImage
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus, Prediction
from app.core import security
from app.api.deps import get_db
import ml.inference.predict

from app.core.config import settings
settings.UPLOAD_DIR = "test_storage_analyses/uploads"
settings.STORAGE_PROVIDER = "local"

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analyses.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db_and_storage():
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree("test_storage_analyses", ignore_errors=True)

@pytest.fixture
def auth_token():
    db = TestingSessionLocal()
    user = User(email="analysis_tester@example.com", password_hash=security.get_password_hash("password123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = security.create_access_token(user.id)
    db.close()
    return {"Authorization": f"Bearer {token}", "user_id": user.id}

@pytest.fixture
def auth_token_user_b():
    db = TestingSessionLocal()
    user = User(email="analysis_userb@example.com", password_hash=security.get_password_hash("password123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = security.create_access_token(user.id)
    db.close()
    return {"Authorization": f"Bearer {token}", "user_id": user.id}

def get_test_image_bytes():
    img = Image.new('RGB', (64, 64), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

@pytest.fixture
def uploaded_image(auth_token):
    response = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token["Authorization"]},
        files={"file": ("test_image.jpg", get_test_image_bytes(), "image/jpeg")}
    )
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def other_user_image(auth_token_user_b):
    response = client.post(
        "/api/images/upload",
        headers={"Authorization": auth_token_user_b["Authorization"]},
        files={"file": ("test_other.jpg", get_test_image_bytes(), "image/jpeg")}
    )
    assert response.status_code == 200
    return response.json()

def test_create_analysis(auth_token, uploaded_image):
    response = client.post(
        f"/api/analyses/images/{uploaded_image['id']}",
        headers={"Authorization": auth_token["Authorization"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["model_version"] == "v1"

    prediction = data.get("prediction")
    assert prediction is not None
    assert len(prediction["probabilities"]) == 10

    total_prob = sum(prediction["probabilities"].values())
    assert 0.99 <= total_prob <= 1.01

    argmax_class = max(prediction["probabilities"], key=prediction["probabilities"].get)
    assert prediction["predicted_class"] == argmax_class
    assert abs(prediction["confidence"] - prediction["probabilities"][argmax_class]) < 1e-5

def test_reject_unauthenticated(uploaded_image):
    response = client.post(f"/api/analyses/images/{uploaded_image['id']}")
    assert response.status_code == 401

def test_reject_another_user_image(auth_token, other_user_image):
    response = client.post(
        f"/api/analyses/images/{other_user_image['id']}",
        headers={"Authorization": auth_token["Authorization"]}
    )
    assert response.status_code == 404

def test_get_analysis_list_and_details(auth_token, uploaded_image):
    create_resp = client.post(f"/api/analyses/images/{uploaded_image['id']}", headers={"Authorization": auth_token["Authorization"]})
    analysis_id = create_resp.json()["id"]

    list_resp = client.get("/api/analyses", headers={"Authorization": auth_token["Authorization"]})
    assert list_resp.status_code == 200
    assert any(item["id"] == analysis_id for item in list_resp.json()["items"])

    detail_resp = client.get(f"/api/analyses/{analysis_id}", headers={"Authorization": auth_token["Authorization"]})
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == analysis_id

def test_reject_access_another_user_analysis(auth_token, auth_token_user_b, uploaded_image):
    create_resp = client.post(f"/api/analyses/images/{uploaded_image['id']}", headers={"Authorization": auth_token["Authorization"]})
    analysis_id = create_resp.json()["id"]

    detail_resp = client.get(f"/api/analyses/{analysis_id}", headers={"Authorization": auth_token_user_b["Authorization"]})
    assert detail_resp.status_code == 404

def test_missing_model_produces_controlled_failure(auth_token, uploaded_image, monkeypatch):
    import app.services.analysis_service as ans
    monkeypatch.setattr(ans, "_predictor", None)
    monkeypatch.setattr(ml.inference.predict, "MODELS_DIR", ml.inference.predict.MODELS_DIR / "fake_dir")

    response = client.post(
        f"/api/analyses/images/{uploaded_image['id']}",
        headers={"Authorization": auth_token["Authorization"]}
    )
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()

    monkeypatch.setattr(ans, "_predictor", None)

def test_invalid_image_produces_controlled_failure(auth_token, uploaded_image, monkeypatch):
    from app.storage import storage_service
    original_predict = ml.inference.predict.LULCPredictor.predict
    def fake_predict(*args, **kwargs):
        raise ValueError("Corrupted image")

    monkeypatch.setattr(ml.inference.predict.LULCPredictor, "predict", fake_predict)

    response = client.post(
        f"/api/analyses/images/{uploaded_image['id']}",
        headers={"Authorization": auth_token["Authorization"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "Corrupted image" in data["error_message"]
