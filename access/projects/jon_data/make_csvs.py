import glob
import os
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import ahocorasick

def make_index_csv():
    museum_numbers = set()
    pn_index_csv = pd.read_csv('indexes/csvs/pn_entries.csv', dtype=str)
    museum_numbers |= set(pn_index_csv['text_number'].astype(str).unique())
    files = os.listdir("database/csvs/")
    for file in files:
        _csv = pd.read_csv("database/csvs/"+file, dtype=str)
        museum_numbers |=  set(_csv['Text'].astype(str).unique())
    df = pd.DataFrame(sorted(museum_numbers), columns=['museum_no'])
    df['artificial_key'] = range(100000, 100000+len(df))
    df['artificial_key'] = 'artkey_' + df['artificial_key'].astype(str)
    def get_alternate_names(x):
        return '; '.join(x['museum_no'].replace('= ', '=').replace(' =', '=').split('='))
    df['alternate_names'] = df.apply(get_alternate_names, axis=1)
    def cbs0issue(x):
        all_names = x['alternate_names'].replace('; ',';').replace(' ;',';').split('; ')
        if '' in all_names:
            all_names.remove('')
        for name in all_names.copy():
            if name[:4] == 'CBS ' and name[:5] != 'CBS 0' and len(name)==8:
                all_names.append('CBS 0'+name[4:])
            if name[:4] == 'Ni. ' and len(name)==9:
                all_names.append('Ist Ni '+name[4:])
            if name[:4] == 'Ni. ' and len(name)<9:
                all_names.append('Ist Ni '+'0'*(9-len(name))+name[4:])
            if name[:3] == '29-':
                all_names.append('UM '+name.replace(' ', ''))
            if name[:4] == 'UET ':
                all_names.append(name[:5]+', '+'0'*(10-len(name.strip()))+name.strip()[6:])
            if name[:4] == 'PBS ':
                if len(name.split(' '))==3:
                    if '/' not in name.split(' ')[1]:
                        all_names.append(name.split(' ')[0]+' '+name.split(' ')[1]+', ' + '0'*(3-len(name.split(' ')[2]))+name.split(' ')[2])
                    else:
                        all_names.append(name.split(' ')[0] + ' 0' + name.split(' ')[1] + ', ' + '0'*(3-len(name.split(' ')[2]))+name.split(' ')[2])
        return '; '.join(all_names)
    df['alternate_names'] = df.apply(cbs0issue, axis=1)
    df['Text'] = df['museum_no']
    df['museum_no'] = df.apply(lambda x: x['museum_no'].replace('= ', '=').replace(' =', '=').split('=')[0], axis=1)
    main_index = pd.read_csv('../../csv_files/index.csv', dtype=str)[['key', 'museum_no', 'alternate_museum_no']]
    main_index['alternate_museum_no'] = main_index['alternate_museum_no'].str.replace('; ',';').replace(' ;',';').str.split(';')
    mi = main_index[['key', 'alternate_museum_no']]
    main_index = main_index.explode('alternate_museum_no')
    main_index = main_index.dropna()
    main_index = main_index.set_index('alternate_museum_no')
    main_index_dict = main_index['key'].to_dict()
    def find_cdli_key(x):
        all_names = x['alternate_names'].replace('; ',';').replace(' ;',';').split(';')
        keys = []
        for name in all_names:
            try:
                keys.append(main_index_dict[name])
            except:
                pass
        if len(keys)>1:
            print('Warning, found multiple keys: ', keys, x) # no such found:)
        if not len(keys):
            return ''
        else:
            return keys[0]
    df['key'] = df.apply(find_cdli_key, axis=1)
    df = df.merge(mi, on='key', how='left')
    df['alternate_museum_no'] = df['alternate_museum_no'].fillna('')
    df['alternate_museum_no'] = df['alternate_museum_no'].apply(lambda x: '; '.join(x))
    df = df[['artificial_key', 'Text', 'museum_no', 'alternate_names', 'key', 'alternate_museum_no']]
    df.to_csv('csv_files/index.csv', index=False)


def make_linked_csv():
    df = pd.read_csv('csv_files/index.csv', dtype=str, index_col='artificial_key')
    df = populate2(df, 'transliterations', 'images\\transliterations_jpgs')
    df = populate2(df, 'cdli_images', 'images\\cdli_images_fixed')
    df = populate2(df, 'photos', 'images\\photos')
    df = df[['transliterations', 'cdli_images', 'photos']]
    df.to_csv('csv_files/linked_resources.csv')


def populate2(df, column, path):
    df[column] = [[] for _ in range(len(df))]
    all_files = glob.glob(path+'/**/*') + glob.glob(path+'/*')
    print(len(all_files))
    files = {x: os.path.basename(x) for x in all_files}
    names = df[['alternate_names']]
    names['alternate_names'] = df['alternate_museum_no'] + '; ' + df['alternate_names']
    names['names'] = names['alternate_names'].str.replace('; ',';').replace(' ;',';').str.split(';').dropna()
    names = names['names'].dropna().to_dict()
    reversed_dict = {}
    for key, value in names.items():
        for v in value:
            reversed_dict.setdefault(v, [])
            reversed_dict[v].append(key)
    names = reversed_dict
    automaton = ahocorasick.Automaton()
    for idx, key in enumerate(names.keys()):
        key = ' '+key+' '
        automaton.add_word(key, (idx, key))
    automaton.make_automaton()
    for w in files.keys():
        for end_index, (insert_order, original_value) in automaton.iter(' '+files[w].replace('_', ' ').replace('.', ' ')):
            for id in names[original_value[1:-1]]:
                df.loc[id][column].append(w)
    df[column] = df[column].apply(lambda x: '; '.join(x))
    return df

# make_index_csv()
# make_linked_csv()