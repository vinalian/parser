import psycopg2
from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text, Command

from magic_filter import F

from telegram_bot import keyboards as KB
from telegram_bot import data_base as DB

import asyncio

from telegram_bot.services import generate_message

router = Router()


@router.message(Command(commands=["start"]))
async def start(message: Message):
    con = DB.User()
    try:
        con.register(message.from_user.username, message.from_user.id)
    except psycopg2.IntegrityError:
        con.cur.close()
    finally:
        con = DB.User()
        user_status = con.get_user_status(message.from_user.id)
        await message.answer(
            'Привет!\n'
            'Этот бот позволяет проверять объявления с сайтов!\n'
            'Выбери нужный тебе сайт',
            reply_markup=KB.main(user_status)
        )


@router.callback_query(Text("on_mailing"))
async def mailing(call: types.CallbackQuery):
    con = DB.User()
    con.set_malling_statys(call.from_user.id, status=1)
    await av_back_to_main(call)


@router.callback_query(Text("off_mailing"))
async def mailing(call: types.CallbackQuery):
    con = DB.User()
    con.set_malling_statys(call.from_user.id, status=0)
    await av_back_to_main(call)


@router.callback_query(Text('backMain'))
async def av_back_to_main(call: types.CallbackQuery):
    con = DB.User()
    user_status = con.get_user_status(call.from_user.id)
    await call.message.edit_text(
        'Вы вернулись в меню!\n'
        'Выбери нужный тебе сайт',
        reply_markup=KB.main(user_status)
    )


@router.callback_query(Text('user_menu'))
async def user_menu(call: types.CallbackQuery):
    con = DB.User()
    sub_status = con.get_sub_status(call.from_user.id)
    await call.message.edit_text(
        f'📱 Ваш профиль:\n'
        f'➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
        f'🔑 ID: {call.from_user.id}\n'
        f'👤 Логин: {call.from_user.username}\n'
        f'➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
        f'💳 Дней подписки: {sub_status if sub_status != "-1" else 0}',
        reply_markup=KB.user_menu(sub_status)
    )


@router.callback_query(Text('malling_settings'))
async def malling_settings(call: types.CallbackQuery):
    con = DB.User()
    user_status = con.get_sub_status(call.from_user.id)
    if user_status != '0' and user_status != '-1':
        await call.message.edit_text(
            'Выберите до 3 моделей авто, чтоб их отслеживать!\n',
            reply_markup=KB.back_main()
        )
    else:
        await call.answer(
            'Доступно только с подпиской!\n',
            show_alert=True
        )


@router.callback_query(Text('favourites'))
async def favourites(call: types.CallbackQuery):
    con = DB.User()
    user_status = con.get_sub_status(call.from_user.id)
    if user_status != '0' and user_status != '-1':
        await call.message.edit_text(
            'Вот ваши избранные объявления:\n',
            reply_markup=KB.back_main()
        )
    else:
        await call.answer(
            'Доступно только с подпиской!\n',
            show_alert=True
        )


@router.callback_query(Text('buy_sub'))
async def buy_sub(call: types.CallbackQuery):
    con = DB.User()
    sub_status = con.get_sub_status(call.from_user.id)
    await call.message.edit_text(
        'Выберите нужный вам срок подписки',
        reply_markup=KB.sub_time(sub_status)
    )


@router.callback_query(KB.Sub_choose.filter(F.action == 'subscribe'))
async def pay_sub(call: types.CallbackQuery, callback_data: KB.Sub_choose):
    await call.message.edit_text(
        'Выберите удобный способ оплаты\n'
        'Внимание! Банковский перевод обрабатывается в течении 24 часов!',
        reply_markup=KB.confirm_sub()
    )


@router.callback_query(Text('av.by'))
async def av_by_menu(call: types.CallbackQuery):
    await call.message.edit_text(
        'Давай выберем марку автомобиля',
        reply_markup=KB.av_choose_brand()
    )


@router.callback_query(KB.Av_choose.filter(F.action == 'av_brand'))
async def av_choose_brand(call: types.CallbackQuery, callback_data: KB.Av_choose):
    await call.message.edit_text(
        'Выбери модель автомобиля',
        reply_markup=KB.av_choose_model(brand=callback_data.data)
    )


@router.callback_query(KB.Av_choose.filter(F.action == 'av_model'))
async def av_choose_model(call: types.CallbackQuery, callback_data: KB.Av_choose):
    con = DB.Connection()
    ann_ids = con.get_ann_ids(model=callback_data.data)
    data = await generate_message(ann_ids)
    await call.message.edit_text(
        'Вот свежие модели:'
    )
    for info in data:
        if info:
            if info['photo']:
                await call.message.answer_photo(
                    photo=info['photo'],
                    caption=f'➧ {info["brand"]} {info["model"]} {info["year"]}г\n'
                            f'➧ Двигатель: {info["engine_type"]}\n'
                            f'➧ Пробег {info["mileage_kb"]} km\n'
                            f'➧ Коробка: {info["transmission"]}\n'
                            f'➧ Кузов: {info["body_type"]}\n'
                            f'➧ Привод:{info["drive_type"]}\n'
                            f'➧ г.{info["location"]}\n'
                            f'➧ 💵 {info["price"]}$\n'
                            f'➧ Дней на продаже: {info["days_on_sale"]} \n'
                            f'➧ {info["description"][:300]}...',
                    reply_markup=KB.link(info["url"])
                )
                await asyncio.sleep(1)
            else:
                await call.message.answer(
                       text=f'➧ 😞 Фото отсутствует\n'
                            f'➧ {info["brand"]} {info["model"]} {info["year"]}г\n'
                            f'➧ Двигатель: {info["engine_type"]}\n'
                            f'➧ Пробег {info["mileage_kb"]} km\n'
                            f'➧ Коробка: {info["transmission"]}\n'
                            f'➧ Кузов: {info["body_type"]}\n'
                            f'➧ Привод:{info["drive_type"]}\n'
                            f'➧ г.{info["location"]}\n'
                            f'➧ 💵 {info["price"]}$\n'
                            f'➧ Дней на продаже: {info["days_on_sale"]} \n'
                            f'➧ {info["description"][:300]}...',
                       reply_markup=KB.link(info["url"])
                )
                await asyncio.sleep(1)

    await call.message.answer(
        'Это все объявления по вашей модели',
        reply_markup=KB.back_main()
    )


@router.callback_query(Text('kufar'))
async def av_by_menu(call: types.CallbackQuery):
    await call.message.edit_text(
        'Выберите марку автомобиля',
        reply_markup=KB.kufar_choose_brand()
    )


@router.callback_query(KB.Kufar_choose.filter(F.action == 'kufar_brand'))
async def av_choose_brand(call: types.CallbackQuery, callback_data: KB.Kufar_choose):
    await call.message.edit_text(
        'Выбери модель автомобиля',
        reply_markup=KB.kufar_choose_model(brand=callback_data.data)
    )


@router.callback_query(KB.Kufar_choose.filter(F.action == 'kufar_model'))
async def av_choose_model(call: types.CallbackQuery, callback_data: KB.Av_choose):
    con = DB.Connection_kufar()
    data = con.get_info_models(model=callback_data.data)
    await call.message.edit_text(
        'Вот свежие модели:'
    )
    for info in data:
        if info[-2] != 'None':
            await call.message.answer_photo(
                photo=info[-2],
                caption=f'➧ Автомобиль: {info[1]}\n'
                        f'➧ Краткая информация: {info[4]}\n'
                        f'➧ Год: {info[5]}\n'
                        f'➧ Пробег: {info[6]}\n'
                        f'➧ Цена: {info[7].split(".")[1][:-2]}\n'
                        f'➧ Город: {info[8]}\n',
                reply_markup=KB.link(info[-3])
            )
        else:
            await call.message.answer(
                text=f'😞 Фото отсутствует :(\n\n'
                     f'➧ Автомобиль {info[1]}\n'
                     f'➧ Краткая информация: {info[4]}\n'
                     f'➧ Год {info[5]}\n'
                     f'➧ Пробег {info[6]}\n'
                     f'➧ Цена: {info[7].split(".")[1][-2]}\n'
                     f'➧ Город: {info[8]}\n',
                reply_markup=KB.link(info[-3])
            )
    await call.message.answer(
        'Это все объявления по вашей модели',
        reply_markup=KB.back_main()
    )
