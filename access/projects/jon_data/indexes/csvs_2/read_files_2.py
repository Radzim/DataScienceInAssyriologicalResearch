import ast
import re
import sqlite3
import docx
import numpy as np
import pickle
import pandas as pd

def text_name_csv(nt_csv):
    d = nt_csv.groupby('text_number')['name'].apply(list).to_dict()
    a = list(d.keys())
    b = list([set(dd) for dd in d.values()])
    df = pd.DataFrame(zip(a, b), columns=['museum_no', 'personal_names'])
    df.to_csv('tablets_to_pns.csv', index=False)

def name_text_csv(nt_csv):
    d = nt_csv.groupby('name')['text_number'].apply(list).to_dict()
    a = list(d.keys())
    b = list([set(filter(lambda x: x == x , dd)) for dd in d.values()])
    df = pd.DataFrame(zip(a, b), columns=['personal_names', 'museum_no'])
    df.to_csv('pns_to_tablets.csv', index=False)

nt_csv = pd.read_csv('pn_entries.csv')[['name', 'text_number']]
pn_csv = pd.read_csv('mbpns.csv')[['Transcription of PN', 'Text']]
pn_csv.columns = ['name', 'text_number']
big_csv = pd.concat([nt_csv, pn_csv])

text_name_csv(big_csv)
name_text_csv(big_csv)