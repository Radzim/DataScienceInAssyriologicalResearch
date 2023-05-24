# import ast
import pickle
import pandas as pd
from pathlib import Path


def load_pickle(filename):
    with open(Path(__file__).parent / ('indexes/pickles/' + filename + '.pickle'), 'rb') as handle:
        return pickle.load(handle)

def load_csv(name, index=None):
    return pd.read_csv(Path(__file__).parent / (name+'.csv'), dtype=str, index_col=index, keep_default_na=False)
