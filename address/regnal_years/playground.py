import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# from analyse_tablet import *
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
# from access import load_data
# from access.projects.jon_data import load_jon_data
#
# print('loading')
#
# index_df = load_data.load_csv('index')
# linked_resources_df = load_data.load_csv('linked_resources')
# cdli_data_df = load_data.load_csv('cdli_data')
#
# pns_to_tablets = load_jon_data.load_csv('indexes/csvs_2/pns_to_tablets', index='personal_names')
# tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
# index_jon = load_jon_data.load_csv('csv_files/index')
# museum_to_artkey = load_jon_data.load_csv('csv_files/index', index='museum_no')
# artkey_to_museum = load_jon_data.load_csv('csv_files/index', index='artificial_key')
# linked_resources_j = load_jon_data.load_csv('csv_files/linked_resources', index='artificial_key')
# museum_to_db = load_jon_data.load_csv('database/csvs/MB Tablet Data Base', index='Text')
#
# print('loading')
# print(tablets_to_pns)
# array = []
# i = 0
# for artkey in artkey_to_museum.index:
#     print(i, '/', len(artkey_to_museum.index))
#     i += 1
#     king_, year_, d = get_partial_date(artkey, (cdli_data_df, index_jon, museum_to_db, kingdb))
#     # if king_ is not None and year_ is not None:
#     _, probability, _, important_names, _, _ = analyse_artkey(artkey, (tablets_to_pns, pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db))
#     pred = np.argmax(probability) + 1000
#     date = None
#     if king_ is not None and year_ is not None:
#         fr, to = int(kingdb.loc[king_]['from']), int(kingdb.loc[king_]['to'])
#         date = fr - (int(year_) - 1)
#     array.append([artkey, king_, year_, len(important_names), date, pred, probability])
# df = pd.DataFrame(array)
# df.columns = ['artkey', 'king_', 'year_', 'n_names', 'date', 'pred', 'probability']
# df.to_pickle('corpus_analysis.pkl')
# print(df)

df = pd.read_pickle('corpus_analysis.pkl')
print(df.columns)
print(df)
# df['diff'] = df['date'] - df['pred']
# for x in df[df['n_names']>0]['diff'].dropna().values:
#     print(str(x)+', ')
# df['n_names'] = np.minimum(df['n_names'], 1)
# print(df[df['king_']==df['king_']][df['year_']==df['year_']].groupby('n_names').count()['diff'])
# print(df[df['king_']==df['king_']][df['year_']==df['year_']].groupby('n_names').mean()['diff'])
# print(df[df['king_']==df['king_']][df['year_']==df['year_']].groupby('n_names').std()['diff'])
# print(df[df['king_']==df['king_']][df['year_']==df['year_']].groupby('n_names').median()['diff'])

# print(len(df[df['king_']==df['king_']][df['year_']==df['year_']]))
# print(len(df[df['king_']==df['king_']][df['year_']!=df['year_']]))
# print(len(df[df['king_']!=df['king_']][df['year_']==df['year_']]))
# print(len(df[df['king_']!=df['king_']][df['year_']!=df['year_']]))
#
# for x in df[df['pred']>1000][df['date']!=df['date']]['pred'].dropna().values:
#     print(str(int(x))+', ')

print(len(df[df['date']==df['date']]))
print(len(df[df['pred']>1000][df['date']!=df['date']]))
print(len(df[df['pred']==1000][df['date']!=df['date']]))
