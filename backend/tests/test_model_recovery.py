import json
import torch
from pathlib import Path
from ml.config import ARTIFACTS_DIR, MODELS_DIR
from ml.models.baseline import get_model
from ml.inference.predict import LULCPredictor

def test_class_mapping_existence_and_format():
    mapping_path = ARTIFACTS_DIR / "class_mapping.json"
    assert mapping_path.exists()
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    
    assert len(mapping) == 10
    assert "0" in mapping
    assert isinstance(mapping["0"], str)

def test_checkpoint_existence_and_loadability():
    model_path = MODELS_DIR / "land_cover" / "v1" / "best_model.pt"
    assert model_path.exists()
    
    # Loadability
    model = get_model(num_classes=10)
    # Check that weights load without errors
    model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
    assert model is not None

def test_inference_on_valid_image():
    from ml.inference.predict import LULCPredictor
    from PIL import Image
    import io
    import json
    dummy = Image.new('RGB', (64, 64), color='green')
    img_byte_arr = io.BytesIO()
    dummy.save(img_byte_arr, format='JPEG')
    
    predictor = LULCPredictor()
    result = predictor.predict(img_byte_arr)
    
    assert "predicted_class" in result
    assert "confidence" in result
    
    with open(ARTIFACTS_DIR / "class_mapping.json", "r") as f:
        mapping = json.load(f)
    valid_classes = list(mapping.values())
    
    assert result["predicted_class"] in valid_classes
    assert 0.0 <= result["confidence"] <= 1.0
