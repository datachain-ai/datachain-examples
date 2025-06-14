import multiprocessing
from torch.utils.data import DataLoader

import datachain as dc
from datachain.lib.pytorch import label_to_int
from src.train import train_model, transform


# Define classes

CLASSES = [
    "Casual",
    "Ethnic",
    "Sports",
    "Formal",
    "Party",
    "Smart Casual",
    "Travel",
    "nan",
]
NUM_CLASSES = len(CLASSES)


# Create a Target column

def add_target_label(usage) -> str:
    return usage if usage in CLASSES else "nan"

if __name__ == '__main__':
    ds = (
        dc.read_dataset("fashion-train")
        .map(target=add_target_label, params=["usage"], output=str)
        .map(label=lambda target: label_to_int(target, CLASSES), output=int)
        .limit(1000) # Take a sample for the DEMO purposes
        .shuffle()
    )

    print(ds.to_pandas().target.value_counts())

    # PyTorch DataLoader with multiprocessing
    train_loader = DataLoader(
        ds.select("file", "label").to_pytorch(transform=transform),
        batch_size=2,
        num_workers=4,  # Use multiple workers for better performance
        # Might need to adjust this depending on your system
        # and if you want to use multiple workers
        multiprocessing_context=multiprocessing.get_context("fork"),
    )
    
    # Train the model
    model, optimizer = train_model(train_loader, NUM_CLASSES, num_epochs=1, lr=0.001)
