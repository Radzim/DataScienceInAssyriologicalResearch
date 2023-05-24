import ast
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from access import load_data
from access.projects.jon_data import load_jon_data

### Maybe this should be moved?
index_df = load_data.load_csv('index')
linked_resources_df = load_data.load_csv('linked_resources')
cdli_data_df = load_data.load_csv('cdli_data')

# def make_kings_list_csv(museum_to_db):
#     names = Counter(museum_to_db["King's name (date of composition)"].values)
#     kingdb = pd.DataFrame(index=names.keys())
#     kingdb['count'] = names.values()
#     kingdb['from'] = ''
#     kingdb['to'] = ''
#     kingdb.to_csv('kinglist.csv')

def analyse_t(query, csvs, exclude):
    cdli_data_df, index_jon, museum_to_db, kingdb = csvs
    munus = index_jon.copy().set_index('artificial_key').loc[query]['alternate_names']
    munus = munus.replace('; ', ';').replace(' ;', ';').split(';')
    dates = []
    string = ''
    certainty = 2
    for munu in munus:
        if munu in museum_to_db.index and munu not in exclude:
            king, year = museum_to_db.loc[munu][["King's name (date of composition)", 'Year']]
            if year == 'accession year':
                year = '1'
            if king in kingdb.index:
                fr, to = kingdb.loc[king]['from'], kingdb.loc[king]['to']
            else:
                fr, to = np.nan, np.nan
            if fr == '' or to == '':
                fr, to = np.nan, np.nan
            if fr==fr and to==to:
                fr, to = int(fr), int(to)
                if year.isnumeric():
                    if fr-(int(year)-1) >= to:
                        dates.append(fr-(int(year)-1))
                        string+= king + ' y. ' + year + ' ('+str(fr-(int(year)-1))+')'
                    else:
                        dates.extend(list(range(to, fr)))
                        string += king + ' y. ?' + ' (' + str(fr) + '-' + str(to) + ')'
                else:
                    dates.extend(list(range(to, fr)))
                    string += king + ' y. ?' + ' (' + str(fr) + '-' + str(to) + ')'
                certainty -= 1
            if fr!=fr or to!=to:
                king = re.sub("\(.*?\)", '', king).replace('?', '').replace('[', '').replace(']', '').strip()
                if king in kingdb.index:
                    fr, to = kingdb.loc[king]['from'], kingdb.loc[king]['to']
                else:
                    fr, to = np.nan, np.nan
                if fr == '' or to == '':
                    fr, to = np.nan, np.nan
                if fr==fr and to==to:
                    fr, to = int(fr), int(to)
                    if year.isnumeric():
                        if fr - (int(year) - 1) >= to:
                            dates.append(fr - (int(year) - 1))
                            string += king + ' y. ' + year + ' (' + str(fr - (int(year) - 1)) + ')'
                        else:
                            dates.extend(list(range(to, fr)))
                            string += king + ' y. ?' + ' (' + str(fr) + '-' + str(to) + ')'
                    else:
                        dates.extend(list(range(to, fr)))
                        string += king + ' (' + str(fr) + '-' + str(to) + ')'
                    certainty = 0
    if certainty % 2:
        string += ' (?)'
    dates = [date-1000 for date in dates]
    d = np.zeros(500)
    if len(dates) > 0:
        d[dates] = 1/len(dates)
    else:
        d = np.array([1/len(d)]*len(d))
    return d, string
    ### ADD CDLI DATA

def get_partial_date(query, csvs):
    cdli_data_df, index_jon, museum_to_db, kingdb = csvs
    munus = index_jon.copy().set_index('artificial_key').loc[query]['alternate_names']
    munus = munus.replace('; ', ';').replace(' ;', ';').split(';')
    king_, year_ = None, None
    for munu in munus:
        if munu in museum_to_db.index:
            king, year = museum_to_db.loc[munu][["King's name (date of composition)", 'Year']]
            if year == 'accession year':
                year = '1'
            if king in kingdb.index:
                fr, to = kingdb.loc[king]['from'], kingdb.loc[king]['to']
            else:
                fr, to = np.nan, np.nan
            if fr == '' or to == '':
                fr, to = np.nan, np.nan
            if fr==fr and to==to:
                king_ = king
                fr, to = int(fr), int(to)
                if year.isnumeric():
                    if fr-(int(year)-1) >= to:
                        year_ = year
                    else:
                        pass
            if fr!=fr or to!=to:
                king = re.sub("\(.*?\)", '', king).replace('?', '').replace('[', '').replace(']', '').strip()
                if king in kingdb.index:
                    fr, to = kingdb.loc[king]['from'], kingdb.loc[king]['to']
                else:
                    fr, to = np.nan, np.nan
                if fr == '' or to == '':
                    fr, to = np.nan, np.nan
                if fr==fr and to==to:
                    king_ = king
                    fr, to = int(fr), int(to)
                    if year.isnumeric():
                        if fr - (int(year) - 1) >= to:
                            year_ = year
                        else:
                            pass
                else:
                    if year.isnumeric():
                        year_ = year
    d = np.zeros(500)
    dates = []
    if year_ is None and king_ is None:
        dates = []
    if year_ is None and king_ is not None:
        fr, to = int(kingdb.loc[king_]['from']), int(kingdb.loc[king_]['to'])
        dates.extend(list(range(int(to), int(fr))))
    if year_ is not None and king_ is not None:
        fr, to = int(kingdb.loc[king_]['from']), int(kingdb.loc[king_]['to'])
        dates.append(fr - (int(year_) - 1))
    if year_ is not None and king_ is None:
        for k in kingdb.index:
            try:
                fr, to = int(kingdb.loc[k]['from']), int(kingdb.loc[k]['to'])
                if int(year_) <= fr-to+1:
                    dates.append(fr - (int(year_) - 1))
            except:
                pass
    dates = [date - 1000 for date in dates]
    if len(dates) > 0:
        d[dates] = 1 / len(dates)
    else:
        d = np.array([1 / len(d)] * len(d))
    d = d*0.9 + 0.1*np.array([1 / len(d)] * len(d))
    return king_, year_, d

def analyse_pn(pn, csvs, exclude):
    pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db, kingdb = csvs
    a = pns_to_tablets.loc[pn]['museum_no']
    tablets = ast.literal_eval(a)
    important_tablets = []
    important_name = False
    timelines = []
    strings = ['<b>'+pn+'</b><br>']
    for tablet in tablets:
        try: #get rid of this
            artkey = museum_to_artkey.loc[tablet]['artificial_key']
            tl, st = analyse_t(artkey, (cdli_data_df, index_jon, museum_to_db, kingdb), exclude)
            if len(st):
                important_name = True
                timelines.append(gaussian_filter1d(tl, 20))
                important_tablets.append(tablet)
                strings.append('<a href="/j/tablet/' + artkey + '">' + tablet + '</a> '+ st + '<br>')
        except:
            pass
    timelines.append([1]*500)
    timelines = np.array(timelines)
    # print(timelines)
    # print(np.sum(timelines, axis=1))
    for i in range(len(timelines)):
        timelines[i] = timelines[i]/sum(timelines[i])
    name_probability = np.sum(timelines + [np.ones(500)/10000], axis=0)
    name_probability = name_probability / sum (name_probability)
    string = ''.join(strings) if important_name else ''
    return name_probability, string, important_name, important_tablets


def load_csv(name, index=None):
    return pd.read_csv(Path(__file__).parent / (name+'.csv'), dtype=str, index_col=index, keep_default_na=False)

kingdb = load_csv('kinglist', index='king')

def analyse_artkey(id, csvs):
    tablets_to_pns, pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db = csvs
    ans = index_jon.copy().set_index('artificial_key').loc[id]['alternate_names'].replace(' ;', ';').replace('; ', ';').split(';')
    pns = set()
    for an in ans:
        try:
            pns|=ast.literal_eval(tablets_to_pns.loc[an]['personal_names'])
        except:
            pass
    pns = list(pns-{''})
    timelines = []
    strings = []
    important_names = []
    important_tablets = []
    for pn in pns:
        nn, st, ip, it = analyse_pn(pn, (pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db, kingdb), ans)
        if ip:
            strings.append(st)
            important_names.append(pn)
            timelines.append(nn)
            important_tablets.extend(it)
    probability = np.prod(timelines+[np.ones(500)], axis=0)
    probability = probability / sum(probability)
    _, partial_date = analyse_t(id, (cdli_data_df, index_jon, museum_to_db, kingdb), id)
    if partial_date == '':
        partial_date = '---'
    return strings, probability, timelines, important_names, important_tablets, partial_date

def analyse_artkey_with_partial_date(id, csvs):
    tablets_to_pns, pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db = csvs
    ans = index_jon.copy().set_index('artificial_key').loc[id]['alternate_names'].replace(' ;', ';').replace('; ', ';').split(';')
    pns = set()
    for an in ans:
        try:
            pns|=ast.literal_eval(tablets_to_pns.loc[an]['personal_names'])
        except:
            pass
    pns = list(pns-{''})
    king_, year_, d_ = get_partial_date(id, (cdli_data_df, index_jon, museum_to_db, kingdb))
    timelines = [d_]
    strings = []
    important_names = []
    important_tablets = []
    for pn in pns:
        nn, st, ip, it = analyse_pn(pn, (pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db, kingdb), ans)
        if ip:
            strings.append(st)
            important_names.append(pn)
            timelines.append(nn)
            important_tablets.extend(it)
    probability = np.prod(timelines+[np.ones(500)], axis=0)
    probability = probability / sum(probability)
    if king_ is None:
        king_ = 'Unknown'
    if year_ is None:
        year_ = 'Unknown'
    partial_date = 'King: ' + king_ + ', Year: ' + year_
    if partial_date == '':
        partial_date = '---'
    return strings, probability, timelines, important_names, important_tablets, partial_date
