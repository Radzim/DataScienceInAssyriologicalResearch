import collections
import glob
import os

import pandas as pd
pd.options.mode.chained_assignment = None


def make_index_csv():
    cdli_csv = pd.read_csv('cdli_data/github_repository/cdli_cat.csv', dtype=str)
    df = cdli_csv[['id_text', 'museum_no', 'accession_no', 'excavation_no', 'ark_number', 'designation', 'primary_publication']]
    df['key'] = 'key_p' + df['id_text']
    # all_mns = []
    def get_all_mns(x):
        blacklist = ['in situ', 'Nimrud', 'unknown', 'IM — or OIM A—', 'not specified by author ', 'Egypt', 'CBS — [] ', 'missing', 'UPenn', 'BM —', 'frag.', 'in situ ', 'frags.', 'missing ', 'OIM L—', 'OIM A—', 'uncertain', 'unnumbered', 'Babylon']
        mn = x['museum_no']

        try:
            if '(' in mn or '+' in mn or ',' in mn:
                mn = mn.replace('formerly', '').replace('was', '').replace('cast', '').replace(',', ';').replace('?', '').replace(':', '').replace('(+)', '+').replace('( +)', '+').replace('(+ )', '+').replace('+', ';').replace('=', '').replace('(', ';').replace(')','').replace(' ;',';').replace(' ;',';').replace(' ;',';').replace('; ',';').replace('; ',';').replace('; ',';')
                mns = mn.split(';')
                mns = [mmm for mmm in mns if len(mmm)>4 and mmm not in blacklist and mmm[-2:] not in [' ?', ' -', ' —']]
                mns = mns + [x['designation'], 'p'+'0'*(6-len(x['id_text']))+x['id_text'], 'P'+'0'*(6-len(x['id_text']))+x['id_text']]
                mns = list(set(mns))
                if '' in mns:
                    mns.remove('')
                # all_mns.extend(mns)
                return '; '.join(mns)
            else:
                mns = [mn]
                mns = [mmm for mmm in mns if len(mmm) > 4 and mmm not in blacklist and mmm[-2:] not in [' ?', ' -', ' —']]
                mns = mns + [x['designation'], 'p'+'0'*(6-len(x['id_text']))+x['id_text'], 'P'+'0'*(6-len(x['id_text']))+x['id_text']]
                mns = list(set(mns))
                if '' in mns:
                    mns.remove('')
                # all_mns.extend(mns)
                return '; '.join(mns)
        except:
            return ''
    df['alternate_museum_no'] = df.apply(get_all_mns, axis=1)
    # print(collections.Counter(all_mns).most_common()[:100])
    # print(df['alternate_museum_no'])
    df.index = df['key']
    df = df.drop('key', axis=1)
    df.to_csv('csv_files/index.csv')


def make_cdli_csv():
    df = pd.read_csv('cdli_data/github_repository/cdli_cat.csv', dtype=str)
    df['key'] = 'key_p' + df['id_text']
    df.index = df['key']
    df = df.drop('key', axis=1)
    df.to_csv('csv_files/cdli_data.csv')


def make_linked_csv():
    df = pd.read_csv('csv_files/index.csv', dtype=str, index_col='key')
    df['cdli_url'] = 'https://cdli.mpiwg-berlin.mpg.de/artifacts/' + df['id_text']
    df = df[['cdli_url']]
    df = populate(df, 'cdli_page', 'cdli_data/cdli_artefact_pages', lambda x: 'key_p'+x[:-4])
    df = populate(df, 'cdli_images', 'cdli_data/cdli_artefact_images', lambda x: 'key_p'+str(int(x[1:-4].split('_')[0])))
    df = populate(df, 'cdli_transliteration_full', 'cdli_data/cdli_artefact_transliterations/full', lambda x: 'key_p'+str(int(x[1:-4])))
    df = populate(df, 'cdli_transliteration_text', 'cdli_data/cdli_artefact_transliterations/text', lambda x: 'key_p'+str(int(x[1:-4].split('_')[0])))
    df = populate(df, 'cdli_transliteration_translations', 'cdli_data/cdli_artefact_transliterations/translations', lambda x: 'key_p'+str(int(x[1:-4].split('_')[0])))
    df.to_csv('csv_files/linked_resources.csv')


def populate(df, column, path, fun):
    df[column] = [[] for _ in range(len(df))]
    files = [os.path.basename(x) for x in glob.glob(path+'/*')]
    for file in files:
        try:
            df.loc[fun(file)][column].append(path+'/'+file)
        except:
            print(file, 'could not be matched.', fun(file), 'not found.')
    df[column] = df[column].apply(lambda x: '; '.join(x))
    return df


# make_index_csv()
# make_cdli_csv()
# make_linked_csv()
