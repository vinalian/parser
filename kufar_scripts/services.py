from kufar_scripts.data_base import Connection


def add_info_to_data_base(a):
    fullname = a.find('h3', class_='styles_title__fsJFl styles_ellipsis__Lt4_3').text
    brand = a.find('h3', class_='styles_title__fsJFl styles_ellipsis__Lt4_3').text.split(' ')[0]
    model = a.find('h3', class_='styles_title__fsJFl styles_ellipsis__Lt4_3').text.split(' ')[1]
    info = a.find('p', class_='styles_params__96mGc styles_ellipsis__Lt4_3').text
    year = a.find('div', class_='styles_year__hzbBk').text
    range = a.find('div', class_='styles_mileage__B_CtT').text
    price = a.find('div', class_='styles_price__O0ZEY').text
    locate = a.find('div', class_='styles_bottom__region__8qEYX').text
    link = a['href']
    car_id = link.split('/')[4].split('?')[0]
    try:
        image = a.find('img', class_="styles_image__H9n5Y lazyload")['data-src']
    except:
        image = None
    if not brand or not model or not info:
        return None
    con = Connection()
    try:
        con.add_new_data(fullname, brand, model, info, year, range, price, locate, link, image, car_id)
    except:
        pass





