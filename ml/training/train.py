import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import json
import time

from ml.config import config, MODELS_DIR
from ml.preprocessing.dataset import get_dataloaders
from ml.models.baseline import get_model

def set_seed(seed):
    import random
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def train_model(smoke_test=False):
    set_seed(config.seed)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    train_loader, val_loader, test_loader, class_mapping = get_dataloaders()
    
    model = get_model(num_classes=len(class_mapping)).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    
    epochs = 1 if smoke_test else config.epochs
    best_val_acc = 0.0
    
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        
        # Training
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        # In smoke test, only run 2 batches
        for i, (images, labels) in enumerate(tqdm(train_loader, desc="Training")):
            if smoke_test and i >= 2: break
            
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        train_loss = running_loss / (i + 1)
        train_acc = correct / total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for i, (images, labels) in enumerate(tqdm(val_loader, desc="Validation")):
                if smoke_test and i >= 2: break
                
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
        val_loss = val_loss / (i + 1)
        val_acc = val_correct / val_total
        
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        # Save best model
        if val_acc > best_val_acc or smoke_test:
            best_val_acc = val_acc
            save_dir = MODELS_DIR / "land_cover" / "v1"
            os.makedirs(save_dir, exist_ok=True)
            model_path = save_dir / "best_model.pt"
            torch.save(model.state_dict(), model_path)
            print(f"Saved new best model to {model_path}")
            
    # Save training metadata
    meta = {
        "dataset": config.dataset_name,
        "num_classes": len(class_mapping),
        "image_size": config.image_size,
        "epochs_trained": epochs,
        "best_val_acc": best_val_acc,
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(MODELS_DIR / "land_cover" / "v1" / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Plot Training Curves
    import matplotlib.pyplot as plt
    from ml.config import ARTIFACTS_DIR
    
    os.makedirs(ARTIFACTS_DIR / "training", exist_ok=True)
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss vs Epoch')
    plt.xlabel('Epoch')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.title('Accuracy vs Epoch')
    plt.xlabel('Epoch')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "training" / "learning_curves.png")
    plt.close()
    
    print("Training complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke-test', action='store_true', help='Run a fast smoke test')
    args = parser.parse_args()
    train_model(smoke_test=args.smoke_test)
