import requests
from bs4 import BeautifulSoup

from kufar_scripts.services import add_info_to_data_base
import threading


def main():
    link = f'https://auto.kufar.by/l/cars'
    resp = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    html = BeautifulSoup(resp.content, 'lxml')
    links_append = 0
    links_skip = 0
    for z, a in enumerate(html.find_all('a', class_='styles_wrapper__xZwyg')):
        if z >= 3:
            add_info_to_data_base(a)
            links_append += 1
        else:
            links_skip += 1
    threading.Timer(60*1, main).start()


if __name__ == '__main__':
    main()
