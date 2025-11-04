import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torch import nn
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from icecream import ic

def train(dataloader, model, loss_func, optimizer):
    size = len(dataloader.dataset)
    model.train(mode=True)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        optimizer.zero_grad()

        y_prediction = model(X)
        loss = loss_func(y_prediction, y)

        loss.backward()
        optimizer.step()

        if batch % 25 == 0:
            loss, current = loss.item(), (batch+1)*len(X)
            print(f"Batch:{batch}|loss: {loss:8f} [{current}|{size}]")

def test(X, y, model):
    model.eval()
    X, y = X.to(device), y.to(device)
    y_pred = model(X)
    y_pred = y_pred.argmax(1)
    y_np = y.cpu().numpy()
    y_pred_np = y_pred.cpu().detach().numpy()

    # Show classification evaluation
    print("\nClassification Report:\n", classification_report(y_np, y_pred_np))

def validate(dataloader, model, loss_func):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)

            y_prediction = model(X)
            test_loss += loss_func(y_prediction, y).item()
            correct += (y_prediction.argmax(1)==y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")


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

class SignWaveNetwork(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(SignWaveNetwork, self).__init__()
        self.linear_ReLU_stack = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.linear_ReLU_stack(x)

if __name__=='__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    BATCH_SIZE = 4
    learning_rate = 1e-4

    dataset_file = "sign_language_test_data.csv"


    df = pd.read_csv(dataset_file)
    X = df.drop(columns=["label"]).values
    input_dim = X.shape[1]


    df_train, df_temp = train_test_split(df, test_size=0.3, random_state=42, stratify=df["label"])  # stratify keeps class balance
    ic(df_train)
    ic(df_temp)
    df_test, df_valid = train_test_split(df_temp, test_size=0.5, random_state=42, stratify=df_temp["label"])
    df_train.to_csv("__train.csv", index=False)
    df_test.to_csv("__test.csv", index=False)
    df_valid.to_csv("__validate.csv", index=False)
    
    train_dataset = SignLanguageDataset("__train.csv", fit=True)
    test_dataset = SignLanguageDataset("__test.csv", 
                                       scaler=train_dataset.scaler,
                                       label_encoder=train_dataset.label_encoder)
    valid_dataset = SignLanguageDataset("__validate.csv", 
                                       scaler=train_dataset.scaler,
                                       label_encoder=train_dataset.label_encoder)


    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=True)
    valid_dataloader = DataLoader(valid_dataset, batch_size=BATCH_SIZE, shuffle=True)


    model = SignWaveNetwork(input_dim, len(train_dataset.label_encoder.classes_)).to(device)
    #onnx_program = torch.onnx.export() # The PI Hat+
    try:
        model.load_state_dict(torch.load("letter_class_model.pth", weights_only=True))
        print("Success")
    except Exception as e:
        print("\n\npth file cannot be found at ./letter_class_model.pth\n\n")

    loss_func = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

    epochs = 5
    for t in range(epochs):
        print(f"Epoch {t+1}\n--------------------------------------------")
        train(train_dataloader, model, loss_func, optimizer)
        validate(valid_dataloader, model, loss_func)



    print("Testing\n--------------------------------------------")
    test(X_test, y_test, model)
    print("Done!")
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
