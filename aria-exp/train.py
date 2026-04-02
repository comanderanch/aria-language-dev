import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

class SimpleDataset(Dataset):
    def __init__(self, path):
        with open(path, "r") as f:
            self.data = f.read().split()

    def __len__(self):
        return len(self.data) - 1

    def __getitem__(self, idx):
        return self.data[idx], self.data[idx + 1]

class DummyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb = nn.Embedding(1000, 64)
        self.fc = nn.Linear(64, 1000)

    def forward(self, x):
        return self.fc(self.emb(x))

def train(args):
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "checkpoints"), exist_ok=True)

    dataset = SimpleDataset(args.data)
    loader = DataLoader(dataset, batch_size=args.batch, shuffle=True)

    model = DummyModel()
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss()

    vocab = {}
    def encode(word):
        if word not in vocab:
            vocab[word] = len(vocab)
        return vocab[word]

    for epoch in range(args.epochs):
        total_loss = 0

        for x, y in loader:
            x = torch.tensor([encode(i) for i in x])
            y = torch.tensor([encode(i) for i in y])

            out = model(x)
            loss = loss_fn(out, y)

            opt.zero_grad()
            loss.backward()
            opt.step()

            total_loss += loss.item()

        print(f"Epoch {epoch} Loss: {total_loss}")

        torch.save(
            model.state_dict(),
            os.path.join(args.out, "checkpoints", f"epoch_{epoch}.pt")
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--save_every", type=int, default=1)
    args = parser.parse_args()

    train(args)
