import os
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, datasets
from ml.config import config, RAW_DIR
from pathlib import Path
import json

def get_transforms(is_training=True):
    if is_training:
        return transforms.Compose([
            transforms.Resize((config.image_size, config.image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((config.image_size, config.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

class SplitDataset(Dataset):
    def __init__(self, root, file_list, class_to_idx, transform=None):
        self.root = Path(root)
        self.file_list = file_list
        self.class_to_idx = class_to_idx
        self.transform = transform
        
    def __len__(self):
        return len(self.file_list)
        
    def __getitem__(self, idx):
        rel_path = self.file_list[idx]
        class_name = Path(rel_path).parent.name
        label = self.class_to_idx[class_name]
        
        from PIL import Image
        img_path = self.root / rel_path
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        return image, label

def get_dataloaders():
    from pathlib import Path
    import random
    from ml.config import ARTIFACTS_DIR
    
    dataset_dir = RAW_DIR / "2750"
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found at {dataset_dir}. Run download script first.")
        
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # Class mapping
    classes = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(dataset_dir / d)])
    class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
    idx_to_class = {i: cls_name for i, cls_name in enumerate(classes)}
    
    with open(ARTIFACTS_DIR / 'class_mapping.json', 'w') as f:
        json.dump(idx_to_class, f, indent=2)
        
    split_file = ARTIFACTS_DIR / "split.json"
    
    if split_file.exists():
        with open(split_file, 'r') as f:
            splits = json.load(f)
        train_files = splits["train"]
        val_files = splits["val"]
        test_files = splits["test"]
    else:
        # Create stratified split
        random.seed(config.seed)
        train_files, val_files, test_files = [], [], []
        
        for cls_name in classes:
            cls_dir = dataset_dir / cls_name
            files = [f for f in os.listdir(cls_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            random.shuffle(files)
            
            n = len(files)
            n_train = int(n * config.train_ratio)
            n_val = int(n * config.val_ratio)
            
            train_files.extend([f"{cls_name}/{f}" for f in files[:n_train]])
            val_files.extend([f"{cls_name}/{f}" for f in files[n_train:n_train+n_val]])
            test_files.extend([f"{cls_name}/{f}" for f in files[n_train+n_val:]])
            
        # Shuffle final lists
        random.shuffle(train_files)
        random.shuffle(val_files)
        random.shuffle(test_files)
        
        with open(split_file, 'w') as f:
            json.dump({
                "train": train_files,
                "val": val_files,
                "test": test_files
            }, f, indent=2)
            
    print(f"Dataset Split -> Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")
            
    train_ds = SplitDataset(dataset_dir, train_files, class_to_idx, get_transforms(is_training=True))
    val_ds = SplitDataset(dataset_dir, val_files, class_to_idx, get_transforms(is_training=False))
    test_ds = SplitDataset(dataset_dir, test_files, class_to_idx, get_transforms(is_training=False))

    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=config.batch_size, shuffle=False)
    
    return train_loader, val_loader, test_loader, idx_to_class
