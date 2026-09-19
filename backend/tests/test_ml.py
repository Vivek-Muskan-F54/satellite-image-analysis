import os
import pytest
import torch
from PIL import Image
import io
import json
import shutil
from ml.config import config, MODELS_DIR, ARTIFACTS_DIR
from ml.models.baseline import get_model
from ml.inference.predict import LULCPredictor
from ml.preprocessing.dataset import get_transforms

@pytest.fixture(scope="function")
def setup_dummy_model(tmp_path, monkeypatch):
    import ml.inference.predict
    
    # Setup dummy artifacts in tmp_path
    dummy_artifacts = tmp_path / "artifacts"
    dummy_models = tmp_path / "models"
    os.makedirs(dummy_artifacts, exist_ok=True)
    os.makedirs(dummy_models / "land_cover" / "v1", exist_ok=True)
    
    # Monkeypatch the module level paths where they are used
    monkeypatch.setattr(ml.inference.predict, "ARTIFACTS_DIR", dummy_artifacts)
    monkeypatch.setattr(ml.inference.predict, "MODELS_DIR", dummy_models)
    
    dummy_mapping = {"0": "Forest", "1": "Water"}
    with open(dummy_artifacts / "class_mapping.json", "w") as f:
        json.dump(dummy_mapping, f)
        
    # Setup dummy model
    model = get_model(num_classes=2, pretrained=False)
    save_dir = dummy_models / "land_cover" / "v1"
    torch.save(model.state_dict(), save_dir / "best_model.pt")
    
    yield

def test_preprocessing_output_shape():
    transform = get_transforms(is_training=False)
    image = Image.new("RGB", (100, 100), color="blue")
    tensor = transform(image)
    
    assert tensor.shape == (3, config.image_size, config.image_size)
    assert isinstance(tensor, torch.Tensor)

def test_inference_pipeline(setup_dummy_model, tmp_path):
    # Create test image
    image_path = tmp_path / "test_img.jpg"
    image = Image.new("RGB", (64, 64), color="green")
    image.save(image_path)
    
    predictor = LULCPredictor(model_version="v1")
    result = predictor.predict(str(image_path))
    
    assert "predicted_class" in result
    assert "confidence" in result
    assert result["predicted_class"] in ["Forest", "Water"]
    assert 0.0 <= result["confidence"] <= 1.0

def test_model_initialization():
    model = get_model(num_classes=10, pretrained=False)
    assert isinstance(model, torch.nn.Module)
    # MobileNetV3 small classifier has output features = num_classes
    assert model.classifier[-1].out_features == 10
