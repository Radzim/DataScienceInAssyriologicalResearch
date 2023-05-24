import os
import time
import pandas as pd
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool


def get_cdli_artefact_page(i, timeout=5):
    if os.path.isfile('cdli_artefact_pages/'+i+'.txt'):
        print(i, 'found')
    else:
        # try:
        #     urllib.request.urlretrieve("https://cdli.mpiwg-berlin.mpg.de/artifacts/"+i, 'cdli_artefact_pages/'+i+'.txt')
        #     print(i, 'downloaded')
        # except:
            print(i, 'failed')
            time.sleep(timeout)


def download_pages(threads=1):
    df = pd.read_csv('github_repository/cdli_cat.csv', dtype=str)
    ids = df.id_text.values
    pool = ThreadPool(threads)
    pool.map(get_cdli_artefact_page, ids)


# download_pages()
