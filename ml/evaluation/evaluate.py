import os
import torch
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from ml.config import config, MODELS_DIR, ARTIFACTS_DIR
from ml.preprocessing.dataset import get_dataloaders
from ml.models.baseline import get_model

def evaluate_model(smoke_test=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    _, _, test_loader, class_mapping = get_dataloaders()
    class_names = [class_mapping[i] for i in range(len(class_mapping))]
    
    model = get_model(num_classes=len(class_mapping), pretrained=False).to(device)
    model_path = MODELS_DIR / "land_cover" / "v1" / "best_model.pt"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Train the model first.")
        
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for i, (images, labels) in enumerate(test_loader):
            if smoke_test and i >= 2: break
            
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    # Calculate metrics
    acc = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    f1_weighted = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    metrics = {
        "accuracy": float(acc),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "weighted_f1": float(f1_weighted)
    }
    
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(ARTIFACTS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("--- Evaluation Metrics ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    # Classification report
    clf_report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True, zero_division=0)
    with open(ARTIFACTS_DIR / "classification_report.json", "w") as f:
        json.dump(clf_report, f, indent=2)
        
    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "confusion_matrix.png")
    plt.close()
    
    print(f"Artifacts saved to {ARTIFACTS_DIR}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke-test', action='store_true', help='Run a fast smoke test')
    args = parser.parse_args()
    evaluate_model(smoke_test=args.smoke_test)
