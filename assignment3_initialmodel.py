# -*- coding: utf-8 -*-
"""assignment3_initialModel.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AYVwxB-_Y_ydsgr2FZEs9Z3dDNU-3Fgv
"""

import pandas as pd
import numpy as np
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import gzip
import plotly.express as px
import torch
import torch.nn as nn
import torch.nn.functional as F
from CustomMINST_Class import CustomMNIST
from FirstNet_Class import FirstNet

def train_loop(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    # Set the model to training mode
    # important for batch normalization and dropout layers
    # Unnecessary in this situation but added for best practices
    model.train()
    # Loop over batches via the dataloader
    for batch, (X, y) in enumerate(dataloader):
        # Compute prediction and loss
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation and looking for improved gradients
        loss.backward()
        optimizer.step()
        # Zeroing out the gradient (otherwise they are summed)
        #   in preparation for next round
        optimizer.zero_grad()

        # Print progress update every few loops
        if batch % 10 == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
def test_loop(dataloader, model, loss_fn):
    # Set the model to evaluation mode
    # important for batch normalization and dropout layers
    # Unnecessary in this situation but added for best practices
    model.eval()
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0

    # Evaluating the model with torch.no_grad() ensures
    # that no gradients are computed during test mode
    # also serves to reduce unnecessary gradient computations
    # and memory usage for tensors with requires_grad=True
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()

    # Printing some output after a testing round
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

# Load our data into memory
train_data = CustomMNIST("train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz")
test_data = CustomMNIST("t10k-images-idx3-ubyte.gz", "t10k-labels-idx1-ubyte.gz")

# Create data feed pipelines for modeling
train_dataloader = DataLoader(train_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

# Check that our data look right when we sample
idx=1
print(f"This image is labeled a {train_data.__getitem__(idx)[1]}")
px.imshow(train_data.__getitem__(idx)[0].reshape(28, 28))

# Create an instance of our model
model = FirstNet()

# Define some training parameters
learning_rate = 1e-2
batch_size = 64
epochs = 50

# Define our loss function
#   This one works for multiclass problems
loss_fn = nn.CrossEntropyLoss()

optimizer = torch.optim.SGD(model.parameters(),lr=learning_rate)

for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train_loop(train_dataloader, model, loss_fn, optimizer)
    test_loop(test_dataloader, model, loss_fn)
print("Done!")

# Specify our path
PATH = "model.pt"

# Create a new "blank" model to load our information into
model = FirstNet()

# Recreate our optimizer
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

# Load back all of our data from the file
checkpoint = torch.load(PATH)
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
EPOCH = checkpoint['epoch']