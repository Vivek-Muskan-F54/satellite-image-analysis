import os
import torch
import torch.nn.functional as F
from PIL import Image
import json
from ml.config import config, MODELS_DIR, ARTIFACTS_DIR
from ml.preprocessing.dataset import get_transforms
from ml.models.baseline import get_model

class LULCPredictor:
    def __init__(self, model_version="v1"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load mapping
        mapping_path = ARTIFACTS_DIR / "class_mapping.json"
        if not mapping_path.exists():
            raise FileNotFoundError(f"Class mapping not found at {mapping_path}")
        with open(mapping_path, 'r') as f:
            self.class_mapping = json.load(f)
        self.idx_to_class = {int(k): v for k, v in self.class_mapping.items()}

        # Load model
        self.model = get_model(num_classes=len(self.class_mapping), pretrained=False).to(self.device)
        model_path = MODELS_DIR / "land_cover" / model_version / "best_model.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")

        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.eval()

        self.transform = get_transforms(is_training=False)

    def predict(self, image_input):
        image = Image.open(image_input).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = F.softmax(outputs, dim=1)
            confidence, predicted = probs.max(1)

            # Map probabilities to class names
            prob_list = probs[0].tolist()
            prob_dict = {self.idx_to_class[i]: float(p) for i, p in enumerate(prob_list)}

        return {
            "predicted_class": self.idx_to_class[predicted.item()],
            "class_index": int(predicted.item()),
            "confidence": float(confidence.item()),
            "probabilities": prob_dict
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=True, help='Path to image')
    args = parser.parse_args()

    predictor = LULCPredictor()
    result = predictor.predict(args.image)
    print(json.dumps(result, indent=2))
