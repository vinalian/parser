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


def main(user_status):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="av.by", callback_data='av.by'))
    kb.row(types.InlineKeyboardButton(text="kufar", callback_data='kufar'))
    if user_status == 0:
        kb.row(types.InlineKeyboardButton(text="Включить рассылку", callback_data='on_mailing'))
    else:
        kb.row(types.InlineKeyboardButton(text="Отключить рассылку", callback_data='off_mailing'))
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
    kb.row(types.InlineKeyboardButton(text="В меню", callback_data='backMain'))
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
    kb.row(types.InlineKeyboardButton(text="В меню", callback_data='backMain'))
    return kb.as_markup()


def link(url):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Перейти к объявлению", url=url, callback_data='#'))
    return kb.as_markup()


def back_main():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="В меню", callback_data='backMain'))
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
    kb.row(types.InlineKeyboardButton(text="В меню", callback_data='backMain'))
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
    kb.row(types.InlineKeyboardButton(text="В меню", callback_data='backMain'))
    return kb.as_markup()
