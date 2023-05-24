from pathlib import Path
import pandas as pd


def load_csv(name):
    return pd.read_csv(Path(__file__).parent / ('csv_files/'+ name+'.csv'), dtype=str, index_col='key', keep_default_na=False)


# index_df = load_csv('index')
# linked_resources_df = load_csv('linked_resources')
# cdli_data_df = load_csv('cdli_data')

def load_text_file(key, column, linked_resources_df):
    file = linked_resources_df.loc[key][column]
    text = ''
    for f in file.replace('; ',';').replace(' ;',';').split('; '):
        if f != '':
            with open(Path(__file__).parent / f, 'r', encoding='utf-8') as ff:
                text += '\n\n<b>' + f.split('/')[-1] + '</b>\n'
                text += ff.read()
    if text == '':
        text += '<b>Not available</b>'
    return text
