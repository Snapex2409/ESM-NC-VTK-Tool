import numpy as np
import json

def read_cols(path, cols=(0, 1)):
    data = np.loadtxt(path, usecols=cols)
    return data

def read_json(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except Exception:
        return None
