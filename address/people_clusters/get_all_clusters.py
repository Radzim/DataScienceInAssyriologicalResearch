import ast
import os
import pickle
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from access.projects.jon_data import load_jon_data

from itertools import chain, combinations
import pandas as pd
pd.options.mode.chained_assignment = None

def load_pickle(filename):
    with open('pickles/' + filename + '.pickle', 'rb') as handle:
        return pickle.load(handle)

def save_pickle(data, filename):
    with open('pickles/' + filename + '.pickle', 'wb') as handle:
        return pickle.dump(data, handle)

# def powerset(iterable):
#     s = list(iterable)
#     print(len(s))
#     r =  chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
#     return sorted([sorted(rr) for rr in r if len(rr)>1])

def twoset(iterable):
    s = list(iterable)
    return sorted([tuple(sorted((ss, rr))) for rr in s for ss in s if ss>rr])

def get_two_set():
    tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
    tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval)
    tablets_to_pns['twoset'] = tablets_to_pns.personal_names.apply(lambda x: list(twoset(x)))
    ttp = tablets_to_pns[['twoset']].explode('twoset').dropna()
    ttp['museum_no'] = ttp.index
    ttp = ttp.groupby('twoset')['museum_no'].apply(list).reset_index(name='numbers')
    ttp['count'] = ttp.numbers.str.len()
    ttp = ttp[ttp['count']>1]
    ttp = ttp.sort_values('count', ascending=False)
    ttp = ttp[['count', 'twoset', 'numbers']]
    ttp = ttp.set_index('twoset')
    return ttp

def one_more_set(s):
    s2 = s.copy()[['numbers']]
    s2 = s2[s2.apply(lambda x: '[' not in ''.join(x.name), axis=1)]
    s2.numbers = s2.numbers.apply(set)
    n = 0
    defs = []
    for i, row in list(s2.iterrows()):
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

# s2 = get_two_set()
# save_pickle(s2, '2')
# print(s2)
# s3 = one_more_set(s2)
# save_pickle(s3, '3')
# print(s3)
# s4 = one_more_set(s3)
# save_pickle(s4, '4')
# print(s4)


#
# s4 = load_pickle('4')
# s5 = one_more_set(s4)
# save_pickle(s5, '5')
# print(s5)

# s2 = load_pickle('2')
# print(s2)
# s3 = one_more_set(s2)
# save_pickle(s3, '3a')
# print(s3)
# s4 = one_more_set(s3)
# save_pickle(s4, '4a')
# print(s4)
# s5 = one_more_set(s4)
# save_pickle(s5, '5a')
# print(s5)

# s3 = load_pickle('3')
# s4 = load_pickle('4')
# s5 = load_pickle('5')
#
# for s in [s2, s3, s4, s5]:
#     print(s)
#     print(len(s))
#     print(len([ss for ss in s.index if '[' not in ''.join(ss)]))

# tuple =
# print(s2.reset_index().index[s2.reset_index().apply(lambda x: 'CBS 8999A' in x.numbers, axis=1)])
# s22 = s2[['numbers']]
# s22.numbers = s22.numbers.apply(set)
# i, row = s22.index[62], s22.iloc[62]
# print(i, row)
# s3 = s22
# s3.numbers = s3.numbers.apply(lambda x: x & row.numbers)
# s3 = s3[s3.numbers.str.len() > 1]
# s3['twoset'] = s3.index
# s3.twoset = s3.twoset.apply(lambda x: tuple(sorted(set(x) | set(i))))
# s3 = s3[s3.twoset.str.len() == len(i) + 1]
# s3 = s3[~s3.index.duplicated(keep='first')]
# print(s3)

def make_t2():
    try:
        t2 = load_pickle('T2')
    except:
        tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
        tablets_to_pns.personal_names = tablets_to_pns.personal_names.apply(ast.literal_eval)
        t2 = tablets_to_pns.copy()
        t2['personal_names'] = t2.apply(lambda x: {xx for xx in x['personal_names'] if '[' not in xx}, axis=1)
        t2['tablets'] = t2.apply(lambda x: {x.name}, axis=1)
        t2 = t2[t2.personal_names.str.len() > 1]
        t2 = t2.reset_index()[['tablets', 'personal_names']]
    return t2

def one_more_t(t):
    t2 = make_t2()
    n = 0
    ts = []
    for i, row in list(t2.iterrows()):
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
#
# t2 = make_t2()
# save_pickle(t2, 'T2')

# t2 = load_pickle('T2')
# t3 = one_more_t(t2)
# print(t3)
# save_pickle(t3, 'T3')

# t3 = load_pickle('T3')
# t4 = one_more_t(t3)
# print(t4)
# save_pickle(t4, 'T4')

# t4 = load_pickle('T4')
# t5 = one_more_t(t4)
# print(t5)
# save_pickle(t5, 'T5')
#
# t5 = load_pickle('T5')
# t6 = one_more_t(t4)
# print(t6)
# save_pickle(t6, 'T6')
#
# t6 = load_pickle('T6')
# t7 = one_more_t(t6)
# print(t7)
# save_pickle(t7, 'T7')
#


s2 = load_pickle('2')
s2 = s2[s2.apply(lambda x: '[' not in ''.join(x.name), axis=1)]
print(s2.head(300).to_string())

def applyfun(x):
    try:
        return ast.literal_eval(x.museum_no)
    except:
        return {}

pns_to_tablets = load_jon_data.load_csv('indexes/csvs_2/pns_to_tablets', index='personal_names')
pns_to_tablets = pns_to_tablets[pns_to_tablets.apply(lambda x: '[' not in x.name, axis=1)]
pns_to_tablets.museum_no = pns_to_tablets.apply(lambda x: applyfun(x), axis=1)
pns_to_tablets['N'] = pns_to_tablets.museum_no.str.len()

to_remove = pns_to_tablets[['N']][pns_to_tablets['N']>=20]

print(to_remove.sort_values('N', ascending=False).to_string())

print(len(to_remove))