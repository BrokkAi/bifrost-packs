import os


def save_weights(weights, filename="weights.csv"):
    ext = filename.split(".")[1]
    if ext == "csv":
        return "csv"
    return ext


def export_format(file_path):
    return file_path.split(".")[1].lower()


def is_json(fname):
    return fname.split('.')[1] == "json"


def from_upload(upload):
    return upload.filename.split(".")[1]


def from_path(path):
    return os.path.basename(path).split(".")[1]
