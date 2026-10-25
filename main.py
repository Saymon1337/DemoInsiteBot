import asyncio
import logging
import socket
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat, TelegramObject, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID
from database.db import init_db, close_db
from database.queries import add_or_update_user
from scenario.loader import seed_scenario_to_db
from handlers import admin_cms, crm_handlers, quiz_engine


class ThrottlingMiddleware(BaseMiddleware):
    """
    Защита от двойных кликов и наложения параллельных запросов от одного пользователя.
    Гарантирует, что следующий клик не начнет менять сессию, пока не завершился предыдущий.
    """
    def __init__(self, rate_limit: float = 0.25):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}
        self.active_users: set[int] = set()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        uid = user.id
        now = time.monotonic()
        last_time = self.users.get(uid, 0.0)

        # Если предыдущий клик этого же юзера еще выполняется или прошло меньше 0.25 сек — гасим дубль
        if uid in self.active_users or (now - last_time < self.rate_limit):
            if isinstance(event, CallbackQuery):
                try:
                    await event.answer()
                except Exception:
                    pass
            return

        self.users[uid] = now
        self.active_users.add(uid)
        try:
            return await handler(event, data)
        finally:
            self.active_users.discard(uid)


async def set_bot_commands(bot: Bot):
    client_commands = [
        BotCommand(command="start", description="Главное меню / Перезапуск"),
        BotCommand(command="contacts", description="Контакты агентства")
    ]
    try:
        await bot.set_my_commands(client_commands, scope=BotCommandScopeDefault())
    except Exception:
        pass

    if OWNER_ID:
        admin_commands = [
            BotCommand(command="start", description="Главное меню / Перезапуск"),
            BotCommand(command="admin", description="Панель управления"),
            BotCommand(command="contacts", description="Контакты агентства")
        ]
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=OWNER_ID))
        except Exception:
            pass


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    logger = logging.getLogger(__name__)

    await init_db()
    await add_or_update_user(tg_id=OWNER_ID, username="owner", full_name="Владелец агентства", default_role="owner")
    await seed_scenario_to_db(force=False)

    # Принудительно используем IPv4 и короткий таймаут (15 сек), чтобы хост никогда не зависал на сокетах
    session = AiohttpSession(timeout=15)
    session._connector_init["family"] = socket.AF_INET

    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.25))

    await set_bot_commands(bot)

    dp.include_router(admin_cms.router)
    dp.include_router(crm_handlers.router)
    dp.include_router(quiz_engine.router)

    logger.info("🚀 Бот IT-агентства запущен (режим высокой стабильности WAL + IPv4)!")
    try:
        await dp.start_polling(bot, polling_timeout=20)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
