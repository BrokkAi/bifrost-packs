import pandas as pd
import torch.nn as nn
import torch.nn.functional as F


def whole_frame(df):
    df = df.copy()
    df.fillna({"Time": "-"}, inplace=True)
    df.dropna(inplace=True)
    return df


def returned_copy(df):
    out = df.dropna()
    return out


def not_inplace(df):
    out = df.dropna(inplace=False)
    return out


def torch_layers(x):
    act = nn.ReLU(inplace=True)
    drop = nn.Dropout(p=0.1, inplace=True)
    y = F.relu(x, inplace=True)
    return act, drop, y
