import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torch import nn
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from icecream import ic

def train(dataloader, model, loss_func, optimizer):
    size = len(dataloader.dataset)
    model.train(mode=True)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        y_prediction = model(X)
        loss = loss_func(y_prediction, y)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

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


class CSVDataset(Dataset):
    def __init__(self, X, y):

        self.X = X.to_numpy().astype("float32") # Last column is target letter
        labels = y.to_numpy().astype("str") # target letter

        # Build mapping from unique letters to integers
        self.classes = sorted(set(labels))
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        
        # Encode targets as integers
        self.y = [self.class_to_idx[lbl] for lbl in labels]

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        X = torch.tensor(self.X[idx])
        y = torch.tensor(self.y[idx], dtype=torch.long)
        return X,y


class NeuralNetwork(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(11, 32),
            nn.Dropout(p=0.3),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.Dropout(p=0.3),
            nn.ReLU(),
            nn.Linear(32, 26)
        )

    def forward(self, X):
        logits = self.linear_relu_stack(X)
        return logits

if __name__=='__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    batch_size = 64
    learning_rate = 1e-4

    dataset_file = "training_data1.csv"

    df = pd.read_csv(dataset_file)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)  # stratify keeps class balance
    X_test, X_valid, y_test, y_valid = train_test_split(X_temp, y_temp, test_size=0.5, random_state=41, stratify=y_temp)
    
    train_dataset = CSVDataset(X_train, y_train)
    test_dataset = CSVDataset(X_test, y_test)
    valid_dataset = CSVDataset(X_valid, y_valid)


    train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=4, shuffle=True)
    valid_dataloader = DataLoader(valid_dataset, batch_size=4, shuffle=True)


    model = NeuralNetwork().to(device)
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
    torch.save(model.state_dict(), "letter_class_model.pth")
    print("Saved PyTorch Model State to letter_class_model.pth")
