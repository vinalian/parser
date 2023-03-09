import requests
from telegram_bot.data_base import Connection, User
import datetime
from threading import Timer


async def generate_message(ann_ids):
    all_messages = []
    if type(ann_ids) == list:
        for ann_id in ann_ids:
            all_messages.append(parse_json_data(requests.get('https://api.av.by/offers/' + ann_id[0],
                                                             headers={'User-Agent': 'Mozilla/5'}).json()))
    else:
        all_messages.append(parse_json_data(requests.get('https://api.av.by/offers/' + ann_ids,
                                                         headers={'User-Agent': 'Mozilla/5'}).json()))
    return all_messages


def parse_json_data(json_data):
    try:
        if json_data['status'] != 'active':
            con = Connection()
            con.delete_ann(json_data['id'])
            return None
    except KeyError:
        return None
    now = datetime.datetime.now()
    ann_date = datetime.datetime.strptime(json_data["refreshedAt"], '%Y-%m-%dT%H:%M:%S+0000')
    if (now - ann_date).days > 15:
        con = Connection()
        con.delete_ann(json_data['id'])
        return None
    message = {}
    try:
        message['description'] = json_data['description']
    except KeyError:
        message['description'] = 'Без описания продавца'
    try:
        message['photo'] = json_data['photos'][0]['big']['url']
    except IndexError:
        message['photo'] = None
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
    message['location'] = json_data['locationName']
    message['days_on_sale'] = json_data['daysOnSale']
    message['price'] = json_data['price']['usd']['amount']
    return message


def get_average_price(brand: str, model: str):
    con = User()
    avg_price = con.get_avg_price(brand, model)
    return avg_price


def generate_ann(info):
    ready_message = []
    if info:
        if info['photo']:
            ready_message.append(f'➧ {info["brand"]} {info["model"]} {info["year"]}г\n'
                                 f'➧ Двигатель: {info["engine_type"]}\n'
                                 f'➧ Пробег {info["mileage_kb"]} km\n'
                                 f'➧ Коробка: {info["transmission"]}\n'
                                 f'➧ Кузов: {info["body_type"]}\n'
                                 f'➧ Привод:{info["drive_type"]}\n'
                                 f'➧ г.{info["location"]}\n'
                                 f'➧ 💵 {info["price"]}$\n'
                                 f'➧ Дней на продаже: {info["days_on_sale"]} \n'
                                 f'➧ {info["description"][:300]}...', )
            ready_message.append(info['photo'])
            ready_message.append(info['url'])
        else:
            ready_message.append(f'➧ 😞 Фото отсутствует\n'
                                 f'➧ {info["brand"]} {info["model"]} {info["year"]}г\n'
                                 f'➧ Двигатель: {info["engine_type"]}\n'
                                 f'➧ Пробег {info["mileage_kb"]} km\n'
                                 f'➧ Коробка: {info["transmission"]}\n'
                                 f'➧ Кузов: {info["body_type"]}\n'
                                 f'➧ Привод:{info["drive_type"]}\n'
                                 f'➧ г.{info["location"]}\n'
                                 f'➧ 💵 {info["price"]}$\n'
                                 f'➧ Дней на продаже: {info["days_on_sale"]} \n'
                                 f'➧ {info["description"][:300]}...', )
            ready_message.append(info['url'])
    return ready_message


def sup_status_editor():
    con = Connection()
    all_subs = con.get_all_sub_status()
    for sub in all_subs:
        con.edit_sub_status(user_id=sub[0],
                            new_sub=str(int(sub[1]) - 1))

    Timer(60*60*24, sup_status_editor).start()
