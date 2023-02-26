from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from telegram_bot import data_base as DB
from aiogram.filters.callback_data import CallbackData


class Av_choose(CallbackData, prefix='a'):
    action: str
    data: str


class Kufar_choose(CallbackData, prefix='k'):
    action: str
    data: str


class Sub_choose(CallbackData, prefix='s'):
    action: str
    time: str
    price: int


class Confirm_bank_transfer(CallbackData, prefix='c'):
    time: str
    action: str
    id: int


class Mailing_brand(CallbackData, prefix='d'):
    action: str
    brand: str


def main(user_status):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚗 av.by", callback_data='av.by'))
    kb.row(types.InlineKeyboardButton(text="🚗 kufar", callback_data='kufar'))
    kb.row(types.InlineKeyboardButton(text="📩 Личный кабинет", callback_data='user_menu'))
    if user_status == 0:
        kb.row(types.InlineKeyboardButton(text="✅ Рассылка выключена", callback_data='on_mailing'))
    else:
        kb.row(types.InlineKeyboardButton(text="❌ Рассылка включена", callback_data='off_mailing'))
    return kb.as_markup()


def user_menu(subscription):
    kb = InlineKeyboardBuilder()
    if subscription == '0' or subscription == '-1':
        kb.row(types.InlineKeyboardButton(text="💳 Купить подписку", callback_data='buy_sub'))
    else:
        kb.row(types.InlineKeyboardButton(text="💳 Продлить подписку", callback_data='buy_sub'))
    kb.row(types.InlineKeyboardButton(text="⚙️ Настойки оповещений", callback_data='malling_settings'))
    kb.row(types.InlineKeyboardButton(text="🌟 Избранные объявления", callback_data='favourites'))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def sub_time(subscription):
    kb = InlineKeyboardBuilder()
    if subscription == '-1':
        kb.row(types.InlineKeyboardButton(text="🎁 1 день - 2р (Ознакомительная)",
                                          callback_data=Sub_choose(action='subscribe', time='1', price=2).pack()))
    kb.row(types.InlineKeyboardButton(text="🔥 7 дней - 20 BYN",
                                      callback_data=Sub_choose(action='subscribe', time='7', price=20).pack()))
    kb.row(types.InlineKeyboardButton(text="🔥 14 дней - 35 BYN",
                                      callback_data=Sub_choose(action='subscribe', time='14', price=35).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def choose_payment_sub():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Банковский перевод", callback_data='bank_transfer'))
    kb.row(types.InlineKeyboardButton(text="Qiwi", callback_data='qiwi'))
    kb.row(types.InlineKeyboardButton(text="Yoomoney", callback_data='Yoomoney'))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def confirm_sub():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Оплатил", callback_data='confirm_sub'))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def confirm_bank_transfer(time, id):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Подтвердить оплату",
                                      callback_data=Confirm_bank_transfer(
                                                                          action='BankTrC',
                                                                          time=time,
                                                                          id=id).pack()))
    return kb.as_markup()


def mailing_user_settings():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Настройки цены", callback_data='mailing_price'))
    kb.row(types.InlineKeyboardButton(text="Избранные бренды", callback_data='mailing_brand'))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def mailing_brand(user_id):
    con = DB.User()
    data = con.get_mailing_brand(user_id)
    kb = InlineKeyboardBuilder()
    try:
        for brand in data.split('*'):
            kb.row(types.InlineKeyboardButton(text=f"{brand}",
                                              callback_data=Mailing_brand(action='del', brand=brand).pack()))
    except AttributeError:
        pass
    kb.row(types.InlineKeyboardButton(text="Добавить бренд", callback_data='add_to_favourites'))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def add_to_favourites(user_id):
    kufar_con = DB.Connection_kufar()
    kufar_data = kufar_con.get_all_brands()
    av_con = DB.Connection()
    av_data = av_con.get_all_brands()
    user_con = DB.User()
    user_data = user_con.get_mailing_brand(user_id).split('*')
    kb = InlineKeyboardBuilder()
    full_data = []
    for a, k in zip(av_data, kufar_data):
        if a[0] not in full_data and a[0] not in user_data:
            full_data.append(a[0])
        if k[0] not in full_data and k[0] not in user_data:
            full_data.append(k[0])
    for z, data in enumerate(sorted(full_data)):
        if z % 3 == 0:
            kb.row(types.InlineKeyboardButton(text=data,
                                              callback_data=Mailing_brand(action='add', brand=data).pack()))
        else:
            kb.add(types.InlineKeyboardButton(text=data,
                                              callback_data=Mailing_brand(action='add', brand=data).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def av_choose_brand():
    con = DB.Connection()
    data = con.get_all_brands()
    kb = InlineKeyboardBuilder()
    for z, brand in enumerate(data):
        if z % 3 == 0:
            kb.row(
                types.InlineKeyboardButton(text=brand[0].title(), callback_data=Av_choose(action='av_brand',
                                                                                          data=brand[0]).pack()))
        else:
            kb.add(types.InlineKeyboardButton(text=brand[0].title(), callback_data=Av_choose(action='av_brand',
                                                                                             data=brand[0]).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def av_choose_model(brand):
    con = DB.Connection()
    data = con.get_model(brand)
    kb = InlineKeyboardBuilder()
    for z, model in enumerate(data):
        if z % 2 == 0:
            kb.row(
                types.InlineKeyboardButton(text=model[0].title(), callback_data=Av_choose(action='av_model',
                                                                                          data=model[0]).pack()))
        else:
            kb.add(
                types.InlineKeyboardButton(text=model[0].title(), callback_data=Av_choose(action='av_model',
                                                                                          data=model[0]).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def link(url):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 Перейти к объявлению", url=url, callback_data='#'))
    return kb.as_markup()


def back_main():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def kufar_choose_brand():
    con = DB.Connection_kufar()
    data = con.get_all_brands()
    kb = InlineKeyboardBuilder()
    for z, brand in enumerate(data):
        if z % 3 == 0:
            kb.row(
                types.InlineKeyboardButton(text=brand[0].title(), callback_data=Kufar_choose(action='kufar_brand',
                                                                                             data=brand[0]).pack()))
        else:
            kb.add(types.InlineKeyboardButton(text=brand[0].title(), callback_data=Kufar_choose(action='kufar_brand',
                                                                                                data=brand[0]).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()


def kufar_choose_model(brand):
    con = DB.Connection_kufar()
    data = con.get_model(brand)
    kb = InlineKeyboardBuilder()
    for z, model in enumerate(data):
        if z % 2 == 0:
            kb.row(
                types.InlineKeyboardButton(text=model[0].title(), callback_data=Kufar_choose(action='kufar_model',
                                                                                             data=model[0]).pack()))
        else:
            kb.add(
                types.InlineKeyboardButton(text=model[0].title(), callback_data=Kufar_choose(action='kufar_model',
                                                                                             data=model[0]).pack()))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data='backMain'))
    return kb.as_markup()
