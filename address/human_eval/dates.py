import ast
import random

import pandas as pd

dfMB = pd.read_csv('../../access/projects/jon_data/database/csvs/MB Tablet Data Base.csv')
dfI = pd.read_csv('../../access/projects/jon_data/csv_files/index.csv')
df2 = dfI.merge(dfMB, left_on='museum_no', right_on='Text')

# df = pd.read_pickle('../regnal_years/corpus_analysis.pkl')
# print(df.columns)
# rows = df[['artkey', 'date', 'pred']].dropna()[df['pred']>1000]
# rows = rows.merge(df2, left_on='artkey', right_on='artificial_key')
# print(rows.sample(n=20, random_state=0)[['artkey', 'museum_no', 'date', 'pred']])

# df = pd.read_pickle('../people_clusters/pickles/2.pickle')
# df['numbers'] = df.apply(lambda x: x['numbers'][:2], axis=1)
# df['t1'] = df['numbers'].str[0]
# df['t2'] = df['numbers'].str[1]
# print(df[['t1', 't2']])
# df = df[df['t1'].isin(dfMB['Text'])]
# df = df[df['t2'].isin(dfMB['Text'])]
# df['names'] = df.index.str.join('; ')
# df = df[~df['names'].str.contains('\[')]
# print(df[['t1', 't2']])
# print(df[['t1', 't2']].sample(n=20, random_state=0).to_string())

df_pt = pd.read_csv('../../access/projects/jon_data/indexes/csvs_2/pns_to_tablets.csv', index_col='personal_names')
for i, row in df_pt.sample(n=100, random_state=0).iterrows():
    try:
        links = ast.literal_eval(row.museum_no)
        if len(links) > 1:
            random.seed(0)
            print(i, random.sample(links, 2))
    except:
        pass
# print(df_pt.apply(lambda x: ast.literal_eval(x['museum_no']), axis=1))
# samples = df_tp.sample(n=20, random_state=0)
# print(df_pt)
