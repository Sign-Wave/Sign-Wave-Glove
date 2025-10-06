import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torch import nn
import polars as pl


class CSVDataset(Dataset):
    def __init__(self, csv_file):
        self.df = pl.read_csv(csv_file)

        self.X = self.df[:,:-1].to_numpy().astype("float32") # Last column is target letter
        self.y = self.df[-1].to_numpy().astype("int32") # target letter

    def __len__(self):
        return self.df.height

    def __getitem__(self, idx):
        X = torch.tensor(self.X[idx])
        y = torch.tensor(self.y[idx])
        return X,y







class NeuralNetwork(nn.Module):
    def __init__(self) -> None:
        super.__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.linear(14, 32),
            nn.Dropout(p=0.3),
            nn.ReLU(),
            nn.linear(32, 32)
            nn.Dropout(p=0.3),
            nn.ReLU(),
            nn.linear(32, 26)
        )

    def forward(self, X):
        logits = self.linear_relu_stack(X)
        return logits

if __name__=='__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    batch_size = 64
    learning_rate = 1e-4

    dataset_file = "training_data1.csv"
    dataset = CSVDataset(dataset_file)

    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
