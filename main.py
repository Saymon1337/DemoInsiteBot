import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat, TelegramObject, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID
from database.db import init_db
from database.queries import add_or_update_user
from scenario.loader import seed_scenario_to_db
from handlers import admin_cms, crm_handlers, quiz_engine

class ThrottlingMiddleware(BaseMiddleware):
    """Защита от двойных кликов и спама запросами (0.3 сек)."""
    def __init__(self, rate_limit: float = 0.3):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            now = time.monotonic()
            last_time = self.users.get(user.id, 0.0)
            if now - last_time < self.rate_limit:
                if isinstance(event, CallbackQuery):
                    await event.answer()
                return
            self.users[user.id] = now
        return await handler(event, data)

async def set_bot_commands(bot: Bot):
    # 1. Чистое меню для всех клиентов (только Старт и Контакты — строго по ТЗ!)
    client_commands = [
        BotCommand(command="start", description="Главное меню / Перезапуск"),
        BotCommand(command="contacts", description="Контакты агентства")
    ]
    await bot.set_my_commands(client_commands, scope=BotCommandScopeDefault())

    # 2. Меню для Владельца (добавлена кнопка /admin)
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

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))

    await set_bot_commands(bot)

    dp.include_router(admin_cms.router)
    dp.include_router(crm_handlers.router)
    dp.include_router(quiz_engine.router)

    logger.info("🚀 Бот IT-агентства запущен с чистым меню!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")