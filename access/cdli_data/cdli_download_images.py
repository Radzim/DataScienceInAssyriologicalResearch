import os
import time
import glob
import requests


def extract_photo_links(text):
    links = []
    for line in text.split('\n'):
        if '<img src="/dl/' in line:
            links.append("https://cdli.mpiwg-berlin.mpg.de/dl/"+line.strip().split('"')[1][7:])
    return links


def get_cdli_artefact_image(image_url,  timeout=5):
    image_name = image_url.split('/')[-1]
    if os.path.isfile('cdli_artefact_images/'+image_name):
        print(image_name, 'found')
    else:
        # try:
        #     img_data = requests.get(image_url).content
        #     with open('cdli_artefact_images/'+image_name, 'wb') as handler:
        #         handler.write(img_data)
        #     print(image_name, 'downloaded')
        # except:
            print(image_name, 'failed')
            time.sleep(timeout)


def process_id(i):
    t = open('cdli_artefact_pages/'+i+'.txt', "r", encoding="utf8").read()
    links = extract_photo_links(t)
    for link in links:
        get_cdli_artefact_image(link)


def download_images(threads=1):
    ids = [str(x[20:-4]) for x in glob.glob("cdli_artefact_pages/*")]
    from multiprocessing.dummy import Pool as ThreadPool
    pool = ThreadPool(threads)
    pool.map(process_id, ids)


def remove_erroneous_files(min_kb=1):
    for file in glob.glob("cdli_artefact_images/*"):
        if os.path.getsize(file) < min_kb * 1024:
            print(file, 'deleted')
            os.remove(file)


# remove_erroneous_files()
# download_images()

