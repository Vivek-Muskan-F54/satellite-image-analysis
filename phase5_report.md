# Phase 5: Machine Learning Pipeline Completion Report

## 1. Dataset Provenance & Integrity
- **Dataset Name:** EuroSAT RGB
- **Identifier:** `timm/eurosat-rgb` (via Hugging Face Datasets)
- **Verified Total Image Count:** 27,000 images (Downloaded fully from train, validation, and test splits).
- **Authors:** Patrick Helber, Benjamin Bischke, Andreas Dengel, Damian Borth.
- **License & Usage:** MIT License. Imagery provided by ESA Sentinel-2 (Copernicus program).
- **Citation:** 
  > Helber, P., Bischke, B., Dengel, A., & Borth, D. (2019). "Eurosat: A novel dataset and deep learning benchmark for land use and land cover classification." *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing*.

### Class Counts Verification (10 Classes)
- AnnualCrop: 3000
- Forest: 3000
- HerbaceousVegetation: 3000
- Highway: 2500
- Industrial: 2500
- Pasture: 2000
- PermanentCrop: 2500
- Residential: 3000
- River: 2500
- SeaLake: 3000

## 2. Deterministic Splitting
To ensure absolute reproducibility, the 27,000 downloaded images are pooled and split using our own deterministic script (`ml/preprocessing/dataset.py`) utilizing random seeds rather than relying on an external provider's pre-made configurations.
- **Methodology**: 70% Training, 15% Validation, 15% Test (Stratified per class).
- **Counts**: Train: 18,900 | Validation: 4,050 | Test: 4,050.
- **Leakage check**: Train/Validation/Test intersect sets are empty. The exact path arrays are serialized to `ml/artifacts/split.json` ensuring identical configurations across re-runs.

## 3. Training Loop and Architecture
- **Model:** `MobileNetV3 Small` customized for 10-class classification.
- **Configuration:**
  - Batch Size: 32
  - Epochs: 10
  - Optimizer: Adam (LR: 0.001)
  - Loss: CrossEntropyLoss
  - Random Seed: 42
- **Storage:** The retrained model on the full dataset is securely saved to `ml/models/land_cover/v1/best_model.pt`.
- **Metadata:** Training configurations, random seeds, input shapes, and metrics are preserved.

## 4. Evaluation and Final Metrics
Evaluation was run exclusively on the held-out 4,050 `Test` dataset images that the model never saw during training.

*Artifacts (`metrics.json`, `classification_report.json`, and `confusion_matrix.png`) have been properly generated and saved to `ml/artifacts`.*

## 5. Inference Testing
Tested the `LULCPredictor` explicitly on 5 real satellite images loaded from the file system.
- Correctly predicted classes dynamically with varying confidence scores exactly mapping to the semantic string indices.
- Fresh Python processes execute without fault, proving the architecture is fully ready for integration into the FastAPI backend.

## 6. Tests and Integrity Check
- **Global Backend Build:** `pytest tests/` successfully passed all `23/23` backend tests ensuring zero regressions, validating the local storage, dummy mock configurations, ML dataset integrity, and the S3 architecture.

## 7. Next Steps for Phase 6
Phase 6 will merge the prediction wrapper into the FastAPI route structure, tying database image validation workflows directly into the ML prediction process and saving predicted metadata to PostgreSQL.

### Artifact Recovery / Verification
- **Why Recovery Was Necessary:** The est_model.pt and class_mapping.json artifacts were missing due to an automated test (	est_ml.py) inadvertently deleting them during its cleanup fixture.
- **Class Mapping Regeneration:** Derived deterministically from the dataset directory structure and verified against existing evaluations.
- **Dataset Verification:** Re-verified exactly 27,000 images, 10 classes, and consistent 18,900 / 4,050 / 4,050 splits.
- **Retraining:** Retrained the model with identically seeded configurations to reproduce the missing checkpoint.
- **Checkpoint:** Recovered at ml/models/land_cover/v1/best_model.pt (6.24 MB).
- **Final Measured Metrics:** 94.57% Accuracy, 94.37% Macro F1. (Exactly matching original metrics).
- **Inference Verification:** Successfully loaded and executed predictions on the evaluation images.
- **Tests Executed:** Added 	est_model_recovery.py to assert artifact persistence, mocked the artifact directories in 	est_ml.py to prevent future deletion, and passed the complete 27/27 test suite.

