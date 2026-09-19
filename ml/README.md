# Machine Learning Pipeline - Land Use / Land Cover Classification

## 1. Architecture
The ML pipeline is fully decoupled from the FastAPI backend and uses a reproducible training workflow.
```
datasets/      # Raw and processed data (git-ignored)
preprocessing/ # Data loading and transformations
training/      # Model training script
evaluation/    # Metrics and visualization
models/        # Saved model weights
inference/     # Single-image prediction pipeline
```

## 2. Dataset
- **Name**: EuroSAT (RGB version)
- **Source**: Sentinel-2 satellite images
- **License**: Open access / Academic usage
- **Classes**: 10 (AnnualCrop, Forest, HerbaceousVegetation, Highway, Industrial, Pasture, PermanentCrop, Residential, River, SeaLake)
- **Dimensions**: 64x64 pixels, 3 channels (RGB)
- **Size**: 27,000 labeled images

### Download
```bash
python -m ml.datasets.download_dataset
```

## 3. Preprocessing
Uses `torchvision.transforms`:
- **Training**: Resize (64x64), RandomHorizontalFlip, RandomVerticalFlip, ToTensor, Normalize(ImageNet stats).
- **Validation/Test**: Resize, ToTensor, Normalize.

## 4. Train/Validation/Test Split
Dataset is randomly split into:
- 70% Training
- 15% Validation
- 15% Testing
A deterministic random seed (`42`) is used to ensure no data leakage.

## 5. Model
**MobileNetV3 Small** (transfer learning).
- Chosen for its high accuracy-to-compute ratio, allowing fast CPU-based inference and training on development machines.
- The classifier head is replaced with a `Linear` layer outputting 10 classes.

## 6. Training
```bash
python -m ml.training.train
# For quick verification:
python -m ml.training.train --smoke-test
```
Tracks CrossEntropyLoss and accuracy. Saves the best model to `ml/models/land_cover/v1/best_model.pt`.

## 7. Evaluation
```bash
python -m ml.evaluation.evaluate
# For quick verification:
python -m ml.evaluation.evaluate --smoke-test
```
Calculates Accuracy, Precision, Recall, Macro/Weighted F1, and a Confusion Matrix.

## 8. Inference
```bash
python -m ml.inference.predict --image <path_to_image>
```
Uses the saved `class_mapping.json` to map model outputs back to human-readable strings.

## 9. Hardware & Limitations
- **CPU/GPU**: Auto-detects CUDA. Falls back to CPU.
- **Limitations**: The pipeline trains on CPU in about 15-20 minutes per epoch. Cloud integration is not yet implemented (Phase 6). No MLflow registry yet.
