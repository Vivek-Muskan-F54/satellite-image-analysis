import os
from dataclasses import dataclass
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
RAW_DIR = DATASETS_DIR / "raw"
PROCESSED_DIR = DATASETS_DIR / "processed"

@dataclass
class MLConfig:
    # Dataset config
    dataset_name: str = "EuroSAT"
    dataset_url: str = "http://madm.dfki.de/files/sentinel/EuroSAT.zip" # Using standard URL
    
    # Preprocessing
    image_size: int = 64
    num_classes: int = 10
    
    # Training
    seed: int = 42
    batch_size: int = 32
    epochs: int = 10
    learning_rate: float = 0.001
    
    # Data splitting
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15

config = MLConfig()
