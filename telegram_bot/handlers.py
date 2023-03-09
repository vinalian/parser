import asyncio
import random
import string

import psycopg2
from aiogram import Router, types
from aiogram.filters import Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from magic_filter import F

import settings
from run_bot import bot
from states import Sub_paying, Edit_mailing_price
from telegram_bot import data_base as DB
from telegram_bot import keyboards as KB
from telegram_bot.services import generate_message, generate_ann
from aiogram.types import LabeledPrice, PreCheckoutQuery

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
async def mailing(call: types.CallbackQuery, state: FSMContext):
    con = DB.User()
    con.set_malling_statys(call.from_user.id, status=1)
    await av_back_to_main(call, state)


@router.callback_query(Text("off_mailing"))
async def mailing(call: types.CallbackQuery, state: FSMContext):
    con = DB.User()
    con.set_malling_statys(call.from_user.id, status=0)
    await av_back_to_main(call, state)


@router.callback_query(Text('backMain'))
async def av_back_to_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
            'Настройте свои уведомления!\n',
            reply_markup=KB.mailing_user_settings()
        )
    else:
        await call.answer(
            'Доступно только с подпиской!\n',
            show_alert=True
        )


@router.callback_query(Text('mailing_price'))
async def mailing_price(call: types.CallbackQuery, state: FSMContext):
    con = DB.User()
    price = con.get_malling_price(call.from_user.id)
    await call.message.edit_text(
        f'Введите минимальное отклонение от средней цены на авто\n'
        f'0 - без отклонения\n'
        f'Установленное минимальное отклонение: {price}%',
        reply_markup=KB.back_main()
    )
    await state.set_state(Edit_mailing_price.price)


@router.message(Edit_mailing_price.price)
async def edit_mailing_price(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except:
        await message.answer('Должно быть числом!', reply_markup=KB.back_main())
        await state.set_state(Edit_mailing_price.price)
        return False
    if 100 < float(message.text) or float(message.text) < 0:
        await message.answer('Должно быть от 0 до 100!', reply_markup=KB.back_main())
        await state.set_state(Edit_mailing_price.price)
        return False
    con = DB.User()
    con.update_malling_price(message.from_user.id, float(message.text))
    await message.answer(
        f'Вы успешно изменены минимальное отклонение\n'
        f'Теперь вы будете получать уведомления, с ценой меньше {message.text}% от средней цены на авто',
        reply_markup=KB.back_main()
    )


@router.callback_query(Text('favourites'))
async def favourites(call: types.CallbackQuery):
    con = DB.User()
    user_status = con.get_sub_status(call.from_user.id)
    favourite = con.get_favourites(call.from_user.id)
    if user_status != '0' and user_status != '-1':
        await call.message.edit_text(
            'Вот ваши избранные объявления:\n',
            reply_markup=KB.back_main()
        )
        if favourite:
            for item in favourite.split('*')[:-1]:
                data = await generate_message(item.split('-')[1])
                if item.split('-')[0] == 'AV':
                    text = generate_ann(data[0])
                    if len(text) == 3:
                        await call.message.answer_photo(
                            photo=text[1],
                            caption=text[0],
                            reply_markup=KB.fav_link(url=text[2],
                                                     ann_id=f"AV-{text[2].split('/')[-1]}")
                        )
                        await asyncio.sleep(1)
                    elif len(text) == 2:
                        await call.message.answer(
                            text=text[0],
                            reply_markup=KB.fav_link(url=text[1],
                                                     ann_id=f"AV-{text[2].split('/')[-1]}")
                        )
                        await asyncio.sleep(1)
                elif item.split('-')[0] == 'Kufar':
                    info = con.get_kufar_fav(item.split('-')[1])
                    if info[-2] != 'None':
                        await call.message.answer_photo(
                            photo=info[-2],
                            caption=f'➧ Автомобиль: {info[1]}\n'
                                    f'➧ Краткая информация: {info[4]}\n'
                                    f'➧ Год: {info[5]}\n'
                                    f'➧ Пробег: {info[6]}\n'
                                    f'➧ Цена: {info[7].split(".")[1][:-2]}\n'
                                    f'➧ Город: {info[8]}\n',
                            reply_markup=KB.fav_link(url=info[-3],
                                                     ann_id=f"Kufar-{info[-3].split('/')[-1].split('?')[0]}")
                        )
                        await asyncio.sleep(1)
                    else:
                        await call.message.answer(
                            text=f'😞 Фото отсутствует :(\n\n'
                                 f'➧ Автомобиль {info[1]}\n'
                                 f'➧ Краткая информация: {info[4]}\n'
                                 f'➧ Год {info[5]}\n'
                                 f'➧ Пробег {info[6]}\n'
                                 f'➧ Цена: {info[7].split(".")[1][-2]}\n'
                                 f'➧ Город: {info[8]}\n',
                            reply_markup=KB.fav_link(url=info[-3],
                                                     ann_id=f"Kufar-{info[-3].split('/').split('?')[0]}"))
                        await asyncio.sleep(1)
            await call.message.answer(
                'Это все ваши избранные объявления!\n',
                reply_markup=KB.back_main()
            )
    else:
        await call.answer(
            'Доступно только с подпиской!\n',
            show_alert=True
        )


@router.callback_query(KB.Add_fav.filter(F.action == 'del_fav'))
async def del_fav(call: types.CallbackQuery, callback_data: KB.Add_fav):
    con = DB.User()
    data = con.get_favourites(call.from_user.id)
    try:
        con.update_favourites(call.from_user.id, f'{data.replace(f"{callback_data.ann_id}*", "")}')
        await call.answer(
            'Удалено!',
            show_alert=True
        )
    except:
        await call.answer(
            'Произошла ошибка!',
            show_alert=True
        )
        con.con.close()


@router.callback_query(Text('buy_sub'))
async def buy_sub(call: types.CallbackQuery, state: FSMContext):
    con = DB.User()
    sub_status = con.get_sub_status(call.from_user.id)
    await call.message.edit_text(
        'Выберите нужный вам срок подписки',
        reply_markup=KB.sub_time(sub_status)
    )
    await state.set_state(Sub_paying.price)


@router.callback_query(KB.Sub_choose.filter(F.action == 'subscribe'))
async def pay_sub(call: types.CallbackQuery, callback_data: KB.Sub_choose, state: FSMContext):
    await state.update_data(price=callback_data.price)
    await state.update_data(time=callback_data.time)
    await call.message.edit_text(
        'Выберите удобный способ оплаты\n'
        'Внимание! Банковский перевод обрабатывается в течении 24 часов!',
        reply_markup=KB.choose_payment_sub()
    )
    await state.set_state(Sub_paying.secret_key)


@router.callback_query(Text('bank_transfer'))
async def bank_transfer(call: types.CallbackQuery, state: FSMContext):
    letters = string.ascii_lowercase + string.ascii_uppercase
    secret_key = ''.join(random.choice(letters) for i in range(15))
    await state.update_data(action=call.data)
    await state.update_data(secret_key=secret_key)
    data = await state.get_data()
    await call.message.edit_text(
        f'Оплата {data["price"]} BYN: \n'
        f'Перевод по номеру счёта:\n'
        f'*Номер счёта*\n'
        f'Сохраните секретный ключ перевода:\n'
        f'{secret_key}',
        reply_markup=KB.confirm_sub()
    )
    await state.set_state(Sub_paying.secret_key)


@router.callback_query(Text('YKassa'))
async def YKassa(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Покупка подписки на {data["time"]} дней',
        description='Покупка подписки в телеграмм боте по парсингу объявлений',
        provider_token=settings.YKassa,
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'{data["time"]} дней подписки',
                amount=data['price']*100*26,
            ),
            LabeledPrice(
                label='НДС',
                amount=data['price']*100*26/100*5
            ),
        ],
        start_parameter='Vios23',
        payload=f'{data["time"]}*'
                f'{call.from_user.id}',
        protect_content=True,
        request_timeout=15
    )


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    con = DB.User()
    con.add_sub(pre_checkout_query.from_user.id, int(pre_checkout_query.invoice_payload.split('*')[0]))


@router.callback_query(Text('confirm_sub'))
async def confirm_sub(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(
        'Ожидайте подтверждения оплаты!',
        reply_markup=KB.back_main()
    )
    await bot.send_message(
        chat_id=settings.ADMIN_ID,
        text=f'Пользователь @{call.from_user.username} с id <{call.from_user.id}>\n'
             f'Совершил оплату {data["price"]} BYN\n'
             f'На {data["time"]} дней подписки'
             f'Через {data["action"]}',
        reply_markup=KB.confirm_bank_transfer(data["time"], call.from_user.id)
    )


@router.callback_query(KB.Confirm_bank_transfer.filter(F.action == 'BankTrC'))
async def confirm_bank_transfer(call: types.CallbackQuery, callback_data: KB.Confirm_bank_transfer):
    con = DB.User()
    con.add_sub(user_id=int(callback_data.id), sub_status=int(callback_data.time))
    await call.message.edit_text(
        f'Вы подтвердили оплату пользователю:\n'
        f'{callback_data.id}'
    )
    await bot.send_message(
        chat_id=callback_data.id,
        text='Вашу оплату подтвердили! Приятного пользования!'
    )


@router.callback_query(Text('mailing_brand'))
async def mailing_brand(call: types.CallbackQuery):
    await call.message.edit_text(
        'Выберите бренд для удаления из оповещений',
        reply_markup=KB.mailing_brand(user_id=call.from_user.id)
    )


@router.callback_query(Text('add_to_mailing'))
async def add_brand_to_mailing(call: types.CallbackQuery):
    con = DB.User()
    mailing_len_brand = con.get_mailing_brand(call.from_user.id).split('*')
    if len(mailing_len_brand) < 6:
        await call.message.edit_text(
            'Выберите бренд для добавления в избранное',
            reply_markup=KB.add_to_mailing(call.from_user.id)
        )
    else:
        await call.answer(
            'Вы достигли лимита в 5 брендов!',
            show_alert=True
        )


@router.callback_query(KB.Mailing_brand.filter(F.action == 'add'))
async def add_to_favourites(call: types.CallbackQuery, callback_data: KB.Mailing_brand):
    con = DB.User()
    con.add_to_mailing(user_id=call.from_user.id, brand=callback_data.brand)
    await call.message.edit_text(
        f'Вы добавили в избранное:\n'
        f'{callback_data.brand}',
        reply_markup=KB.back_main()
    )


@router.callback_query(KB.Mailing_brand.filter(F.action == 'del'))
async def delete_mailing_brand(call: types.CallbackQuery, callback_data: KB.Mailing_brand):
    con = DB.User()
    con.delete_mailing_brand(user_id=call.from_user.id, brand=callback_data.brand)
    await call.message.edit_text(
        'Вы успешно удалили бренд из списка оповещений',
        reply_markup=KB.back_main()
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
    if data:
        for info in data:
            text = generate_ann(info)
            if len(text) == 3:
                await call.message.answer_photo(
                    photo=text[1],
                    caption=text[0],
                    reply_markup=KB.link(url=text[2],
                                         ann_id=f"AV-{text[2].split('/')[-1]}")
                )
                await asyncio.sleep(1)
            elif len(text) == 2:
                await call.message.answer(
                    text=text[0],
                    reply_markup=KB.link(text[1],
                                         ann_id=f"AV-{text[2].split('/')[-1]}")
                )
                await asyncio.sleep(1)
            else:
                pass
    await call.message.answer(
        'Это все объявления по вашей модели',
        reply_markup=KB.back_main()
    )


@router.callback_query(KB.Add_fav.filter(F.action == 'add_to_fav'))
async def add_to_favourites(call: types.CallbackQuery, callback_data: KB.Add_fav):
    con = DB.User()
    data = con.get_favourites(user_id=call.from_user.id)
    if len(data.split('*')) <= 10:
        if callback_data.ann_id not in data:
            data += f'{callback_data.ann_id}*'
            con.update_favourites(user_id=call.from_user.id, ann_id=data)
            await call.answer(
                'Добавлено в избранное',
                show_alert=True
            )
        else:
            await call.answer(
                'Уже в избранном!',
                show_alert=True
            )
    else:
        await call.answer(
            'Вы достигли лимита в 10 объявлений!',
            show_alert=True
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
                reply_markup=KB.link(url=info[-3],
                                     ann_id=f"Kufar-{info[-3].split('/')[-1].split('?')[0]}")
            )
            await asyncio.sleep(1)
        else:
            await call.message.answer(
                text=f'😞 Фото отсутствует :(\n\n'
                     f'➧ Автомобиль {info[1]}\n'
                     f'➧ Краткая информация: {info[4]}\n'
                     f'➧ Год {info[5]}\n'
                     f'➧ Пробег {info[6]}\n'
                     f'➧ Цена: {info[7].split(".")[1][-2]}\n'
                     f'➧ Город: {info[8]}\n',
                reply_markup=KB.link(info[-3],
                                     ann_id=f"Kufar-{info[-3].split('/').split('?')[0]}"))
            await asyncio.sleep(1)
    await call.message.answer(
        'Это все объявления по вашей модели',
        reply_markup=KB.back_main()
    )
