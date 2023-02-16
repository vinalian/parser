import asyncio
from aiogram import Bot, Dispatcher

import settings
from telegram_bot import handlers


bot = Bot(token=settings.token)
dp = Dispatcher()


async def main():
    #add router
    dp.include_router(handlers.router)

    #disables the event handler when the bot is turned off
    await bot.delete_webhook(drop_pending_updates=True)

    #turning on the endless work of the bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

