import json
from pathlib import Path
from ml.config import ARTIFACTS_DIR

def test_split_integrity():
    split_file = ARTIFACTS_DIR / "split.json"
    assert split_file.exists(), "Split file must exist"
    
    with open(split_file, 'r') as f:
        splits = json.load(f)
        
    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])
    
    # Check zero overlap
    assert len(train_set.intersection(val_set)) == 0, "Leakage between train and val"
    assert len(train_set.intersection(test_set)) == 0, "Leakage between train and test"
    assert len(val_set.intersection(test_set)) == 0, "Leakage between val and test"
    
    # Check total size
    assert len(train_set) + len(val_set) + len(test_set) == 27000, "Dataset must have exactly 27000 images"
    
    # Check reproducibility (should match exactly 70/15/15)
    assert len(train_set) == 18900
    assert len(val_set) == 4050
    assert len(test_set) == 4050
