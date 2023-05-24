import ast
import os
import pickle
import sys

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from access.projects.jon_data import load_jon_data

def load_pickle(filename):
    with open('pickles_clusters/' + filename + '.pickle', 'rb') as handle:
        return pickle.load(handle)

def save_pickle(data, filename):
    with open('pickles_clusters/' + filename + '.pickle', 'wb') as handle:
        return pickle.dump(data, handle)

def get_common_names(max_=20):
    def applyfun(x):
        try:
            return ast.literal_eval(x.museum_no)
        except:
            return {}

    pns_to_tablets = load_jon_data.load_csv('indexes/csvs_2/pns_to_tablets', index='personal_names')
    # pns_to_tablets = pns_to_tablets[pns_to_tablets.apply(lambda x: '[' not in x.name, axis=1)]
    pns_to_tablets.museum_no = pns_to_tablets.apply(lambda x: applyfun(x), axis=1)
    pns_to_tablets['N'] = pns_to_tablets.museum_no.str.len()

    to_remove = pns_to_tablets[['N']][pns_to_tablets['N'] >= max_]
    print(to_remove.sort_values('N'))
    return list(to_remove.index)

def make_t2():
    tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
    tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval)
    t2 = tablets_to_pns.copy()
    t2['personal_names'] = t2.apply(lambda x: {xx for xx in x['personal_names'] if '[' not in xx}, axis=1)
    rn = get_common_names()
    t2['personal_names'] = t2.apply(lambda x: {xx for xx in x['personal_names'] if xx not in rn}, axis=1)
    t2['tablets'] = t2.apply(lambda x: {x.name}, axis=1)
    t2 = t2[t2.personal_names.str.len() > 1]
    t2 = t2.reset_index()[['tablets', 'personal_names']]
    save_pickle(t2, 'T2')
    return t2

def one_more_t(t):
    t2 = make_t2()
    n = 0
    ts = []
    for i, row in list(t2.iterrows()):
        if n%100 == 0:
            print(n, '/', len(t2))
        n += 1
        t22 = t.copy()
        t22.personal_names = t22.personal_names.apply(lambda x: x & row.personal_names)
        t22.tablets = t22.tablets.apply(lambda x: x | row.tablets)
        t22 = t22[t22.personal_names.str.len() > 1]
        t22 = t22[t22.tablets.str.len() > len(t.iloc[0].tablets)]
        ts.append(t22)
    df22 = pd.concat(ts)
    df22 = df22[~df22.tablets.duplicated(keep='first')]
    df22.reset_index(drop=True, inplace=True)
    return df22

def make_s2():
    def twoset(iterable):
        s = list(iterable)
        return sorted([tuple(sorted((ss, rr))) for rr in s for ss in s if ss > rr])
    tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
    tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval)

    rn = get_common_names()
    tablets_to_pns['personal_names'] = tablets_to_pns.apply(lambda x: {xx for xx in x['personal_names'] if xx not in rn}, axis=1)

    tablets_to_pns['twoset'] = tablets_to_pns.personal_names.apply(lambda x: list(twoset(x)))
    ttp = tablets_to_pns[['twoset']].explode('twoset').dropna()
    ttp['museum_no'] = ttp.index
    ttp = ttp.groupby('twoset')['museum_no'].apply(list).reset_index(name='numbers')
    ttp['count'] = ttp.numbers.str.len()
    ttp = ttp[ttp['count']>1]
    ttp = ttp.sort_values('count', ascending=False)
    ttp = ttp[['count', 'twoset', 'numbers']]
    ttp = ttp.set_index('twoset')
    ttp = ttp[ttp.apply(lambda x: '[' not in ''.join(x.name), axis=1)]
    return ttp

def one_more_s(s):
    s2 = s.copy()[['numbers']]
    s2.numbers = s2.numbers.apply(set)
    n = 0
    defs = []
    for i, row in list(s2.iterrows()):
        if n%100 == 0:
            print(n, '/', len(s2))
        n+=1
        s3 = s2.copy()
        s3.numbers = s3.numbers.apply(lambda x: x & row.numbers)
        s3 = s3[s3.numbers.str.len() > 0]
        s3['twoset'] = s3.index
        s3.twoset = s3.twoset.apply(lambda x: tuple(sorted(set(x) | set(i))))
        s3 = s3[s3.twoset.str.len() == len(i) + 1]
        s3.index = s3.twoset
        s3 = s3[~s3.index.duplicated(keep='first')]
        s3 = s3[s3.numbers.str.len() > 1]
        defs.append(s3[['numbers']])
    s3_ = pd.concat(defs)
    s3_ = s3_[~s3_.index.duplicated(keep='first')]
    return s3_

def make_s_through_n(n=4):
    s_ = make_s2()
    n_ = 2
    for i in range(n):
        print(s_)
        save_pickle(s_, 'S'+str(n_))
        s_ = one_more_s(s_)
        n_ += 1

def make_t_through_n(n=10):
    t_ = make_t2()
    n_ = 2
    for i in range(n):
        print(t_)
        save_pickle(t_, 'T'+str(n_))
        t_ = one_more_t(t_)
        n_ += 1

# make_t_through_n()



# tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
# tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval).str.len()
# print(tablets_to_pns.sort_values('personal_names', ascending=False))
#
# print(get_common_names())

# count_non_repeating()

# x = load_pickle('T6')
# x['n'] = x.personal_names.str.len()
# print(x.sort_values('n').tail(20).to_string())

# query = ['UM 29-15-11', 'UM 29-13-776', 'BE 15 198', 'CBS 8999A', 'UM 29-13-443']
# tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
# for q in query:
#

# make_s_through_n(n=10)
# for i in range(2, 5):
#     t = load_pickle('S'+str(i))
#     print(t.numbers.value_counts().head(20))
#

def count_non_repeating():
    try:
        load_pickle('overview')
        # raise Exception
    except:
        all_rows = []
        for i in range(3, 11):
            try:
                t = load_pickle('T'+str(i))
                t_n = load_pickle('T'+str(i+1))
                t['personal_names'] = t['personal_names'].astype(str)
                t_n['personal_names'] = t_n['personal_names'].astype(str)
                t0 = load_pickle('T' + str(i))
                t0 = t0[t.personal_names.apply(lambda x: x not in list(t_n['personal_names']))]
                t0.reset_index(drop=True, inplace=True)
            except:
                t0 = load_pickle('T'+str(i))
            # print(t0)
            all_rows.append(t0)
            # print(len(t))
            # print(t)
        pc = pd.concat(all_rows)
        pc.reset_index(drop=True, inplace=True)
        pc['n_t'] = pc.tablets.str.len()
        pc['n_p'] = pc.personal_names.str.len()
        pc = pc.sort_values(['n_t', 'n_p'])
        pc['id'] = pc.index.astype(str)
        def unique(row):
            for set2, id in zip(pc.tablets, pc.id):
                if len(row.tablets - set2) == 0:
                    if row.id != id:
                        return False
            return True
        def label(row):
            names = []
            for set2, id, u in zip(pc.tablets, pc.id, pc.unique):
                if len(row.tablets - set2) == 0:
                    if row.id != id and u:
                        names.append('\Cref{sec:'+id+'}')
            if len(names):
                return 'These tablets are included in a larger set, see: ' + ', '.join(names) + '.'
            return ''
        pc['unique'] = pc.apply(unique, axis=1)
        pc['label'] = pc.apply(label, axis=1)
        save_pickle(pc, 'overview')
    tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
    tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval)
    pc = load_pickle('overview')
    # pc = pc[pc.n_p + pc.n_t > 5]
    text = []
    current_ch = 0
    current_sec = 0
    text.append('\setcounter{chapter}{1}')
    def short(xx):
        return xx.split('(', 1)[0]
    for i, row in pc.iterrows():
        if row.n_t != current_ch:
            current_sec = 0
            current_ch = row.n_t
            text.append('')
            text.append('\chapter{'+str(current_ch)+' Tablets}')
        if row.n_p != current_sec:
            current_sec = row.n_p
            text.append('')
            text.append('\setcounter{section}{'+str(current_sec-1)+'}\section{'+str(current_sec)+' Names}')
        text.append('')
        text.append('\subsection{'+', '.join(row.tablets)+'}\label{sec:'+row.id+'}')
        text.append('')
        if len(row.label):
            text.append('Names in common: ' + ', '.join(row.personal_names).replace('&', '\&'))
            text.append('')
            text.append('\\textit{'+row.label+'}')
        else:
            all_names_dict = {tablet: tablets_to_pns.loc[tablet].personal_names for tablet in row.tablets}
            all_names = list(set().union(*all_names_dict.values()))
            make_df = pd.DataFrame(index=all_names, columns=row.tablets)
            for tablet in row.tablets:
                make_df[tablet] = ['\\textbf{\checkmark}' if a in all_names_dict[tablet] else None for a in all_names]
            make_df['count'] = make_df.apply(lambda x: x.notnull().sum(), axis='columns')
            make_df = make_df.fillna('')
            make_df = make_df.sort_values('count', ascending=False)
            make_df = make_df[make_df['count']>1]
            make_df = make_df.drop('count', axis=1)
            remember = set(make_df.index)
            make_df.index = ['\\textbf{'+short(xx).replace('[', '').replace(']', '').replace('&', '\&').replace('%', '\%')+'}' for xx in make_df.index]
            make_df.columns = ['\\textbf{'+c+'}' for c in make_df.columns]
            text.append('\\textbf{Repeated names:}')
            text.append('')
            text.append(make_df.style.to_latex().replace('tabular', 'longtable'))
            text.append('\\textbf{Single names:}')
            text.append('')
            for tablet in row.tablets:
                text.append('')
                text.append('\\textbf{'+tablet+'}')
                text.append(', '.join(all_names_dict[tablet]-remember).replace('&', '\&').replace('%', '\%'))
                text.append('')
            text.append('')
    print(len(text))
    with open('tex/body.tex', 'w', encoding="utf-8") as f:
        f.write('\n'.join(text))

# count_non_repeating()
print(load_pickle('overview')[load_pickle('overview')['label']==''])