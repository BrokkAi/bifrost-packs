import pandas as pd


def clean(df):
    out = df.dropna(inplace=True)
    return out


def sort_frame(df):
    return df.sort_values("a", inplace=True)


def chained_call(df):
    df = df.reset_index(drop=True, inplace=True).rename(columns=str)
    return df


def rename_index(index, names):
    index = index.set_names(names, inplace=True)
    return index
