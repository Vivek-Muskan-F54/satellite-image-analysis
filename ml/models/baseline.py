import torch.nn as nn
from torchvision import models
from ml.config import config

def get_model(num_classes=config.num_classes, pretrained=True):
    """
    Returns a lightweight transfer-learning CNN (MobileNetV3 Small).
    MobileNetV3 is extremely fast on CPU while providing strong baseline accuracy.
    """
    # Use MobileNet V3 Small for fast CPU baseline
    weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = models.mobilenet_v3_small(weights=weights)
    
    # Replace classifier head for our num_classes
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    
    return model
