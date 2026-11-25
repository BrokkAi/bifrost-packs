import pandas as pd


def assign_back(stats):
    stats["Time"] = stats["Time"].fillna("-")
    return stats


def whole_frame(df):
    df = df.copy()
    df.fillna({"Time": "-"}, inplace=True)
    df.dropna(inplace=True)
    return df


def frames_in_list(frames):
    for i in range(len(frames)):
        frames[i].dropna(inplace=True)
    return frames


def column_without_inplace(df):
    df["x"] = df["x"].clip(lower=0)
    return df.loc[df["x"] > 0].dropna()


def dict_of_frames(frames):
    frames["train"].dropna(inplace=True)
    frames["test"].reset_index(drop=True, inplace=True)
    return frames
