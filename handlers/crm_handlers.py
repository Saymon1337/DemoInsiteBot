import html
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database.queries import update_lead_status, get_lead_by_code
from keyboards.engine_kb import get_lead_card_kb

router = Router()
logger = logging.getLogger(__name__)

# ----------------- 1. ФИНАЛЬНАЯ НАВИГАЦИЯ КЛИЕНТА (стр. 24 ТЗ) -----------------

@router.callback_query(F.data == "btn_nav_main")
async def nav_to_main(callback: CallbackQuery):
    await callback.answer()
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, "main_menu", callback=callback)

@router.callback_query(F.data == "btn_nav_portfolio")
async def nav_to_portfolio(callback: CallbackQuery):
    await callback.answer()
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, "portfolio_spheres", callback=callback)

@router.callback_query(F.data == "btn_nav_contacts")
async def nav_to_contacts(callback: CallbackQuery):
    await callback.answer()
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, "contacts_screen", callback=callback)

# ----------------- 2. МЕНЕДЖЕРСКИЕ КНОПКИ MINI-CRM -----------------

CRM_STATUS_MAP = {
    "take": ("🟡 В РАБОТЕ", "in_progress", "Вы взяли лид в работу!"),
    "call": ("📞 СОЗВОН НАЗНАЧЕН", "meeting_scheduled", "Статус: созвон назначен"),
    "deal": ("🟢 ДОГОВОР ПОДПИСАН", "deal_closed", "Поздравляем с закрытием сделки! 🎉"),
    "reject": ("🔴 ОТКАЗ / НЕЦЕЛЕВОЙ", "rejected", "Лид отмечен как отказ.")
}

@router.callback_query(F.data.startswith("crm_"))
async def handle_crm_status_change(callback: CallbackQuery):
    action, lead_code = callback.data.split(":")
    action_key = action.replace("crm_", "")
    
    if action_key not in CRM_STATUS_MAP:
        await callback.answer()
        return

    status_label, db_status, alert_text = CRM_STATUS_MAP[action_key]
    manager = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    # 1. Обновляем статус заявки в SQLite базе
    await update_lead_status(lead_code=lead_code, status=db_status, manager_name=manager)
    await callback.answer(alert_text, show_alert=True)

    # 2. Обновляем текст карточки в чате менеджеров в реальном времени
    current_text = callback.message.text or callback.message.caption or ""
    
    # Отрезаем старую плашку статуса, если она уже была
    if "\n\n📌 СТАТУС В CRM:" in current_text:
        base_text = current_text.split("\n\n📌 СТАТУС В CRM:")[0]
    else:
        base_text = current_text

    updated_card_text = (
        f"{base_text}\n\n"
        f"📌 СТАТУС В CRM: <b>{status_label}</b>\n"
        f"👨‍💼 Ответственный: <b>{html.escape(manager)}</b>"
    )

    try:
        # Если статус финальный (сделка или отказ) — убираем кнопки, иначе оставляем для смены шага
        new_kb = None if db_status in ("deal_closed", "rejected") else get_lead_card_kb(lead_code)
        
        if callback.message.caption:
            await callback.message.edit_caption(caption=updated_card_text, reply_markup=new_kb, parse_mode="HTML")
        else:
            await callback.message.edit_text(text=updated_card_text, reply_markup=new_kb, parse_mode="HTML")
    except TelegramBadRequest:
        pass