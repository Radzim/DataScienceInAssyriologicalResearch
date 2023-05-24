import ast
import os
import sys
from json import dumps

import numpy as np
import pandas as pd
from django.http import FileResponse
from django.shortcuts import render

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from access import load_data
from access.projects.jon_data import load_jon_data
from address.regnal_years.analyse_tablet import analyse_artkey, analyse_artkey_with_partial_date

### Maybe this should be moved?
index_df = load_data.load_csv('index')
linked_resources_df = load_data.load_csv('linked_resources')
cdli_data_df = load_data.load_csv('cdli_data')

pns_to_tablets = load_jon_data.load_csv('indexes/csvs_2/pns_to_tablets', index='personal_names')
tablets_to_pns = load_jon_data.load_csv('indexes/csvs_2/tablets_to_pns', index='museum_no')
# pns_to_tablets = load_jon_data.load_csv('indexes/csvs/pns_to_tablets', index='personal_names')
# tablets_to_pns = load_jon_data.load_csv('indexes/csvs/tablets_to_pns', index='museum_no')
index_jon = load_jon_data.load_csv('csv_files/index')
museum_to_artkey = load_jon_data.load_csv('csv_files/index', index='museum_no')
artkey_to_museum = load_jon_data.load_csv('csv_files/index', index='artificial_key')
linked_resources_j = load_jon_data.load_csv('csv_files/linked_resources', index='artificial_key')
museum_to_db = load_jon_data.load_csv('database/csvs/MB Tablet Data Base', index='Text')

big_index = pd.merge(index_jon[['artificial_key', 'Text', 'museum_no', 'alternate_names', 'key']],index_df[['museum_no', 'alternate_museum_no']], on='key', how='outer')
big_index['museum_no'] = big_index['museum_no_x'].fillna(big_index['museum_no_y'])
big_index['key'] = big_index['artificial_key'].fillna(big_index['key'])
big_index['all_names'] = big_index['alternate_names'].fillna('').str.replace('; ', ';').replace(' ;', ';').str.split(';') + big_index['alternate_museum_no'].fillna('').str.replace('; ', ';').replace(' ;', ';').str.split(';')
big_index['all_names'] = big_index['all_names'].apply(lambda x: [xx for xx in x if xx]).str.join('; ')
big_index = big_index[['key', 'museum_no', 'all_names']]
###

def index(request):
    return render(request, 'djangoapp/index.html', {'subtitle': 'assyrian tablets'})

def j_regnal(request, artkey='key_p1'):
    strings, probability, timelines, important_names, important_tablets, partial_date = analyse_artkey(artkey, (tablets_to_pns, pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db))

    mn = artkey_to_museum.loc[artkey].museum_no
    try:
        names = ast.literal_eval(tablets_to_pns.loc[mn].personal_names)
    except:
        names = important_names
    data = []
    nodes = [
        {
            'name': mn,
            'id': artkey,
            'marker': {'radius': 30},
            'type': 'tablet',
            'color': '#ffb57c',
        }
    ]
    for name in names:
        data.append([artkey, 'pn_' + name])
        color_node = '#7cb5ec' if name in important_names else '#aaaaaa'
        nodes.append({
            'name': name,
            'id': 'pn_' + name,
            'marker': {'radius': 10},
            'type': 'person',
            'color': color_node,
        })
    for mn_t in important_tablets:
        key_t = museum_to_artkey.loc[mn_t].artificial_key
        names_t = ast.literal_eval(tablets_to_pns.loc[mn_t].personal_names)
        for name_t in names_t:
            if name_t in important_names:
                data.append([key_t, 'pn_' + name_t])
        nodes.append({
            'name': mn_t,
            'id': key_t,
            'marker': {'radius': 20},
            'type': 'tablet',
            'color': '#ecb57c',
        })
    series0 = [{
        'name': 'Combined',
        'data': [list(i) for i in zip(list(range(1000,1500)), list(probability.round(6)))],
        'dashStyle': 'Solid',
        'color': '#000000',
        'fillColor': '#000000'
    }]
    series = [{
                'name': important_names[i],
                'data': [list(i) for i in zip(list(range(1000,1500)), list(timelines[i].round(6)))],
                'dashStyle': 'shortdot'
            } for i in range(len(important_names))]
    ticks = list(range(1000,1500, 100))

    ####
    _, probability_, timelines_, _, _, partial_date = analyse_artkey_with_partial_date(artkey, (tablets_to_pns, pns_to_tablets, museum_to_artkey, cdli_data_df, index_jon, museum_to_db))
    series2 = [{
        'name': 'Combined',
        'data': [list(i) for i in zip(list(range(1000,1500)), list(probability_.round(6)))],
        'dashStyle': 'Solid',
        'color': '#000000',
        'fillColor': '#000000'
    },
        {
            'name': 'Partial Date',
            'data': [list(i) for i in zip(list(range(1000, 1500)), list(timelines_[0].round(6)))],
            'dashStyle': 'dot',
            'color': '#FF0000',
            'fillColor': '#FF0000'
        },
    ]
    series3 = [{
                'name': important_names[i],
                'data': [list(i) for i in zip(list(range(1000,1500)), list(timelines_[i+1].round(6)))],
                'dashStyle': 'shortdot'
            } for i in range(len(important_names))]
    ####

    context = {'strings': strings, 'timelines':timelines, 'name': mn, 'id': artkey, "data": dumps(data), "nodes": dumps(nodes), "series": dumps(series0 + series), "series2": dumps(series2 + series3), 'ticks': dumps(ticks), 'partial_date': partial_date}
    return render(request, 'djangoapp/regnal.html', context=context)

# @user_passes_test(access_check)
def j_graph(request, artkey='key_p1'):
    mn = artkey_to_museum.loc[artkey].museum_no
    try:
        names = ast.literal_eval(tablets_to_pns.loc[mn].personal_names)
    except:
        names = []
    data = []
    nodes = [
        {
            'name': mn,
            'id': artkey,
            'marker': {'radius': 30},
            'type': 'tablet',
            'color': '#ffb57c',
        }
    ]
    tablets = set()
    for name in names:
        tts = ast.literal_eval(pns_to_tablets.loc[name].museum_no)
        if len(tts) < 10:
            data.append([artkey, 'pn_' + name])
            nodes.append({
                'name': name,
                'id': 'pn_' + name,
                'marker': {'radius': 10},
                'type': 'person',
                'color': '#7cb5ec',
            })
            tablets |= tts
    duplicate_names = {}
    for mn_t in tablets:
        key_t = museum_to_artkey.loc[mn_t].artificial_key
        names_t = ast.literal_eval(tablets_to_pns.loc[mn_t].personal_names)
        for name_t in names_t:
            if name_t in duplicate_names:
                data.append([key_t, 'pn_' + name_t])
                data.append([duplicate_names[name_t], 'pn_' + name_t])
                nodes.append({
                    'name': name_t,
                    'id': 'pn_' + name_t,
                    'marker': {'radius': 10},
                    'type': 'person',
                    'color': '#7cb5ec'
                })
            else:
                duplicate_names[name_t] = key_t
        nodes.append({
            'name': mn_t,
            'id': key_t,
            'marker': {'radius': 20},
            'type': 'tablet',
            'color': '#ecb57c',
        })
    context = {'name': mn, 'id': artkey, "data": dumps(data), "nodes": dumps(nodes)}
    return render(request, 'djangoapp/graph.html', context=context)

# @user_passes_test(access_check)
def j_tablet(request, artkey='key_p1'):
        if artkey[:4] == 'key_':
            return tablet(request, artkey)
        key = artkey_to_museum.loc[artkey]['key']
        if key != '':
            images = linked_resources_df.loc[key]['cdli_images'].replace('; ',';').replace(' ;',';').split(';')
            cdli_text = cdli_data_df.loc[key].to_string()
            tablet_info = index_df.loc[key].to_string()
            cdli_transcription = load_data.load_text_file(key, 'cdli_transliteration_text', linked_resources_df)
            cdli_translation = load_data.load_text_file(key, 'cdli_transliteration_translations', linked_resources_df)
        else:
            images = ['']
            cdli_text = '<b>Not available</b>'
            tablet_info = '<b>Not available</b>'
            cdli_transcription = '<b>Not available</b>'
            cdli_translation = '<b>Not available</b>'
        museum_n = artkey_to_museum.loc[artkey]['museum_no']
        images2 = linked_resources_j.loc[artkey]['cdli_images'].replace('; ',';').replace(' ;',';').split(';')
        images_transliterations = linked_resources_j.loc[artkey]['transliterations'].replace('; ',';').replace(' ;',';').split(';')
        images_photos = linked_resources_j.loc[artkey]['photos'].replace('; ', ';').replace(' ;',';').split(';')
        try:
            jon_text = museum_to_db.loc[museum_n].to_string()
        except:
            jon_text = '<b>Not available</b>'

        try:
            pns = ast.literal_eval(tablets_to_pns.loc[museum_n].personal_names)
        except:
            pns = set()
        related_tablets = []
        personal_names = []
        pns = sorted(pns, key=lambda x: -len(ast.literal_eval(pns_to_tablets.loc[x].museum_no)))
        for name in pns:
            temptablets = list(ast.literal_eval(pns_to_tablets.loc[name].museum_no) - {museum_n})
            related_tablets.extend(temptablets + ['']*max(0, 1-len(temptablets)) + [''])
            personal_names.extend([name] + ['']*(len(temptablets)-1) + [''])
        related_tablets = ['' if x=='' else {'mn': x, 'id': museum_to_artkey.loc[x]['artificial_key']} for x in related_tablets]

        return render(request, 'djangoapp/jtablet.html', {
            'cdli_data': cdli_text,
            'jon_data': jon_text,
            'images': images,
            'images2': images2,
            'images_transliterations': images_transliterations,
            'images_photos': images_photos,
            'tablet_name': artkey,
            'museum_no': museum_n,
            'tablet_info': tablet_info,
            'cdli_transcription': cdli_transcription,
            'cdli_translation': cdli_translation,
            'personal_names': personal_names,
            'related_tablets': related_tablets
        })

def tablet(request, key='key_p1'):
    images = linked_resources_df.loc[key]['cdli_images'].replace('; ',';').replace(' ;',';').split(';')
    cdli_text = cdli_data_df.loc[key].to_string()
    tablet_info = index_df.loc[key].to_string()
    cdli_transcription = load_data.load_text_file(key, 'cdli_transliteration_text', linked_resources_df)
    cdli_translation = load_data.load_text_file(key, 'cdli_transliteration_translations', linked_resources_df)
    return render(request, 'djangoapp/tablet.html', {
        'cdli_data': cdli_text,
        'images':images,
        'tablet_name': key,
        'museum_no':index_df.loc[key]['museum_no'],
        'tablet_info': tablet_info,
        'cdli_transcription': cdli_transcription,
        'cdli_translation': cdli_translation,
    })

def overview(request):
    search_term = request.GET.get("q")
    n = int(request.GET.get("n"))
    offset = int(request.GET.get("offset"))
    indexes = big_index.index[big_index['all_names'].str.contains(search_term, case=False, na=False)]
    total = len(indexes)
    indexes = indexes[offset:min(offset+n, len(indexes))]
    articles = big_index.loc[indexes]
    return render(request, 'djangoapp/overview.html', {'articles': articles, 'search_term': search_term, 'n': n, 'offset': offset, "m": n+offset, 'total': total})

def keyboards(request):
    return render(request, 'djangoapp/keyboards.html', {})

def download_keyboard(request, name='cunei'):
    file = open('../../KeyboardLayouts/'+name+'.zip', 'rb')
    return FileResponse(file, as_attachment=True, filename=name+'.zip')