import requests
from telegram_bot.data_base import Connection
import datetime


async def generate_message(ann_ids):
    all_messages = []
    for ann_id in ann_ids:
        all_messages.append(parse_json_data(requests.get('https://api.av.by/offers/' + ann_id[0],
                                                         headers={'User-Agent': 'Mozilla/5'}).json()))
    return all_messages


def parse_json_data(json_data):
    if json_data['status'] != 'active':
        con = Connection()
        con.delete_ann(json_data['id'])
        return None
    now = datetime.datetime.now()
    ann_date = datetime.datetime.strptime(json_data["refreshedAt"], '%Y-%m-%dT%H:%M:%S+0000')
    if (now-ann_date).days > 15:
        con = Connection()
        con.delete_ann(json_data['id'])
        return None
    message = {}
    message['days_on_sale'] = json_data['daysOnSale']
    message['description'] = json_data['description']
    message['location'] = json_data['locationName']
    message['photo'] = json_data['photos'][0]['big']['url']
    message['price'] = json_data['price']['usd']['amount']
    for i in json_data['properties']:
        match i['name']:
            case 'brand':
                message['brand'] = i['value']
            case 'model':
                message['model'] = i['value']
            case 'engine_type':
                message['engine_type'] = i['value']
            case 'transmission_type':
                message['transmission'] = i['value']
            case 'body_type':
                message['body_type'] = i['value']
            case 'mileage_km':
                message['mileage_kb'] = i['value']
            case 'drive_type':
                message['drive_type'] = i['value']
    message['year'] = json_data['metadata']['year']
    message['url'] = json_data['publicUrl']
    return message














