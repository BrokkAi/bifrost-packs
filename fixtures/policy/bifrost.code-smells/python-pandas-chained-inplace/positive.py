import pandas as pd


def fill_time(stats):
    stats["Time"].fillna("-", inplace=True)
    return stats


def clip_rows(df, mask):
    df.loc[mask, "x"].clip(lower=0, inplace=True)
    df.iloc[:, 0].replace(0, 1, inplace=True)
    return df
