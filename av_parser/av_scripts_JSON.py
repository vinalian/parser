from bs4 import BeautifulSoup
from av_parser.services import get_annotation_id, check_request, add_ann_to_db, get_json_data
import threading


def main():
    url = 'https://cars.av.by/filter?sort=4'
    response = check_request(url)
    html = BeautifulSoup(response.content, 'lxml')
    data = html.find('div', class_='listing__items').find_all('div', class_='listing-item')
    all_ids = get_annotation_id(data)
    json_data = get_json_data(all_ids)
    threading.Timer(60*10, main).start()


if __name__ == '__main__':
    main()
