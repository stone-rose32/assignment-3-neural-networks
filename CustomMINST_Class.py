# -*- coding: utf-8 -*-
"""Untitled6.ipynb

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

class CustomMNIST(Dataset):
    def __init__(self, gzip_images, gzip_labels):
        # read in our raw data from the hosting URL
        self.gzip_images = gzip_images
        self.gzip_labels = gzip_labels
        with gzip.open(self.gzip_labels, 'rb') as f:
          self.label_data = np.frombuffer(f.read(), dtype='uint8', offset = 8)
          self.label_data = pd.DataFrame(data=self.label_data.reshape(len(self.label_data),1))
          self.label_data.columns = ["Labels"]

        with gzip.open(self.gzip_images, 'rb') as f:
          self.image_data = np.frombuffer(f.read(), dtype='uint8', offset = 16)
          self.image_data = pd.DataFrame(data=self.image_data.reshape(len(self.label_data),784))

        self.raw_data = pd.concat([self.label_data, self.image_data], axis = 1)

    # return the length of the complete data set
    #   to be used in internal calculations for pytorch
    def __len__(self):
        return self.raw_data.shape[0]

    # retrieve a single record based on index position `idx`
    def __getitem__(self, idx):
        # extract the image separate from the label
        image = self.raw_data.iloc[idx, 1:].values.reshape(1, 28, 28)
        # Specify dtype to align with default dtype used by weight matrices
        image = torch.tensor(image, dtype=torch.float32)
        # extract the label
        label = torch.tensor(self.raw_data.iloc[idx, 0])

        # return the image and its corresponding label
        return image, label

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

def train_net(model, train_dataloader, test_dataloader, epochs=5, learning_rate=1e-3, batch_size=64):
    # Define some training parameters
    lr = learning_rate
    bs = batch_size
    ep = epochs

    # Define our loss function
    #   This one works for multiclass problems
    loss_fn = nn.CrossEntropyLoss()

    # Build our optimizer with the parameters from
    #   the model we defined, and the learning rate
    #   that we picked
    optimizer = torch.optim.SGD(model.parameters(),
        lr=lr)

    # Need to repeat the training process for each epoch.
    #   In each epoch, the model will eventually see EVERY
    #   observations in the data
    for t in range(ep):
        try:
            print(f"Epoch {model.EPOCH+t+1}\n-------------------------------")
        except:
            print(f"Epoch {t+1}\n-------------------------------")
        train_loop(train_dataloader, model, loss_fn, optimizer)
        test_loop(test_dataloader, model, loss_fn)
    print("Done!")

    try:
        model.EPOCH += ep
    except:
        model.EPOCH = ep

    return model