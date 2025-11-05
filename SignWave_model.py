#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ---------------------------
# Config
# ---------------------------
#@TODO change
CSV_FILE = "sign_language_data.csv"
BATCH_SIZE = 64 if torch.cuda.is_available() else 4
EPOCHS = 30
LR = 1e-3
CONF_THRESHOLD = 0.75   # confidence threshold for "relax"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------------------
# Dataset
# ---------------------------
class SignLanguageDataset(Dataset):
    def __init__(self, csv_file, scaler=None, label_encoder=None, fit=False):
        df = pd.read_csv(csv_file)
        X = df.drop(columns=["label"]).values.astype(np.float32)
        y = df["label"].values

        # Encode labels (A–Z)
        if fit:
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(y)
        else:
            self.label_encoder = label_encoder
            y = self.label_encoder.transform(y)

        # Normalize features
        if fit:
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)
        else:
            self.scaler = scaler
            X = self.scaler.transform(X)

        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ---------------------------
# Model
# ---------------------------
class SignWaveNetwork(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(SignWaveNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.net(x)

# ---------------------------
# Training
# ---------------------------
def train_model():
    # Load dataset
    df = pd.read_csv(CSV_FILE)
    X = df.drop(columns=["label"]).values
    input_dim = X.shape[1]

    # Split train/val
    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
    train_df.to_csv("_train.csv", index=False)
    val_df.to_csv("_val.csv", index=False)

    # Fit label encoder and scaler on training set
    train_ds = SignLanguageDataset("_train.csv", fit=True)
    val_ds = SignLanguageDataset("_val.csv",
                                 scaler=train_ds.scaler,
                                 label_encoder=train_ds.label_encoder)

    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    # Model
    model = SignWaveNetwork(input_dim, len(train_ds.label_encoder.classes_)).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    # Training loop
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for Xb, yb in train_dl:
            Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            out = model(Xb)
            loss = criterion(out, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(train_dl)

        # Validation accuracy
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for Xb, yb in val_dl:
                Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
                preds = model(Xb).argmax(dim=1)
                correct += (preds == yb).sum().item()
                total += len(yb)
        acc = correct / total
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.4f} | Val Acc: {acc:.3f}")

    # Save model + metadata
    torch.save({
        "model_state": model.state_dict(),
        "scaler": train_ds.scaler,
        "label_encoder": train_ds.label_encoder,
        "input_dim": input_dim,
    }, "signwave_model.pth")

    print("")
    print("*----------------------------------*")
    print("|Model saved as 'signwave_model.pth'|")
    print("*----------------------------------*")
    return model, train_ds.scaler, train_ds.label_encoder

# ---------------------------
# Inference
# ---------------------------
def load_model(path="signwave_model.pth"):
    ckpt = torch.load(path, map_location=DEVICE)
    model = SignWaveNetwork(ckpt["input_dim"], len(ckpt["label_encoder"].classes_))
    model.load_state_dict(ckpt["model_state"])
    model.to(DEVICE)
    model.eval()
    return model, ckpt["scaler"], ckpt["label_encoder"]

def predict(model, scaler, label_encoder, data_row, threshold=CONF_THRESHOLD):
    """
    data_row: list or np.array of shape (num_features,)
    """
    x = np.array(data_row, dtype=np.float32).reshape(1, -1)
    x = scaler.transform(x)
    x = torch.tensor(x, dtype=torch.float32).to(DEVICE)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1).cpu().numpy().flatten()
        conf = probs.max()
        pred_idx = probs.argmax()
        pred_label = label_encoder.inverse_transform([pred_idx])[0]
        if conf < threshold:
            return "relax", conf
        return pred_label, conf

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    # Train model
    model, scaler, le = train_model()

    # Example inference on one sample (using same CSV)
    df = pd.read_csv(CSV_FILE)
    sample = df.drop(columns=["label"]).iloc[0].values
    pred, conf = predict(model, scaler, le, sample)
    print(f"\nPrediction: {pred}  (confidence: {conf:.2f})")

