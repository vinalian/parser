import psycopg2
import requests

from av_parser.data_base import Connection


def check_request(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print(f'[AV.by][ERROR] response status code: {response.status_code} Please try again')
    return response


def get_annotation_id(data):
    all_ids = []
    for item in data:
        annotation_id = item.find('a', class_='listing-item__link').get('href')
        all_ids.append(annotation_id.split('/')[-1])
    return all_ids


def get_json_data(all_ids: list):
    api_url = 'https://api.av.by/offers/'
    for ann_id in all_ids:
        add_ann_to_db(requests.get(api_url + ann_id, headers={'User-Agent': 'Mozilla/5'}).json())
        add_ann_to_archive(requests.get(api_url + ann_id, headers={'User-Agent': 'Mozilla/5'}).json())
    print(f'[AV.by][INFO] Loading...')


def add_ann_to_db(json_data):
    brand = None
    model = None
    for i in json_data['properties']:
        match i['name']:
            case 'brand':
                brand = i['value']
            case 'model':
                model = i['value']
    ann_id = json_data['id']
    category = json_data['advertType']
    con = Connection()
    if json_data['metadata']['condition']['label'] == 'с пробегом' or json_data['metadata']['condition']['label'] == 'новый':
        try:
            con.add_new_ann(brand, model, ann_id, category)
            print(f'[AV.by][INFO] {ann_id} added to database')
        except psycopg2.errors.UniqueViolation:
            print(f'[AV.by][ERROR] {ann_id} already exists in database')
        finally:
            con.cur.close()
    else:
        print(f'[AV.by][WARNING] {ann_id} state is not "с пробегом" or "новый". Link https://api.av.by/offers/{ann_id}')


def add_ann_to_archive(json_data):
    brand = None
    model = None
    price = None
    for i in json_data['properties']:
        match i['name']:
            case 'brand':
                brand = i['value']
            case 'model':
                model = i['value']
    ann_id = json_data['id']
    price = json_data['price']['usd']['amount']
    con = Connection()
    print(brand, model, price, ann_id)
    if price and brand and model:
        try:
            con.add_to_archive(brand, model, ann_id, price)
            print(f'[AV.by][INFO] {ann_id} added to archive')
        except psycopg2.errors.UniqueViolation:
            print(f'[AV.by][ERROR] {ann_id} already exists in archive')
        finally:
            con.cur.close()
