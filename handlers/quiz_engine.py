import html
import re
import logging
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, BotCommandScopeChat
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from config import OWNER_ID
from database.queries import (
    get_node, get_node_buttons, get_or_create_session,
    update_session_node, pop_session_history, toggle_multiselect_option,
    save_session_answer, reset_session, get_user_permissions,
    get_user_profile, save_user_profile, add_or_update_user
)
from keyboards.engine_kb import build_node_keyboard

router = Router()
logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r"^[\+]?[0-9\s\-\(\)]{10,18}$")

def is_valid_link(text: str) -> bool:
    t = text.strip()
    if re.match(r"^@[a-zA-Z0-9_]{3,32}$", t):
        return True
    url_pattern = re.compile(
        r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Zа-яА-Я]{2,63}(/.*)?$",
        re.IGNORECASE
    )
    return bool(url_pattern.match(t))

async def render_node(bot, user_id: int, node_id: str, message: Message = None, callback: CallbackQuery = None, force_client_view: bool = False):
    if node_id == "final_lead_name":
        profile = await get_user_profile(user_id)
        if profile and profile.get("phone") and profile.get("saved_name"):
            await save_session_answer(user_id, "final_lead_name", profile["saved_name"])
            await save_session_answer(user_id, "final_lead_phone", profile["phone"])
            node_id = "final_lead_messenger"
            await update_session_node(user_id, "final_lead_messenger", push_history=True)

    node = await get_node(node_id)
    if not node:
        node = await get_node("main_menu")
        node_id = "main_menu"

    if not node:
        node = {
            "id": "main_menu",
            "text": "👋 <b>Главное меню</b>\n\nВыберите интересующее направление:",
            "node_type": "regular"
        }
        node_id = "main_menu"

    buttons = await get_node_buttons(node_id)
    session = await get_or_create_session(user_id)
    perms = await get_user_permissions(user_id)
    
    # Флаги режима отображения
    has_admin = bool(perms.get("can_content") or perms.get("is_owner"))
    is_admin = False if force_client_view else has_admin
    is_client_preview = bool(force_client_view and has_admin)

    saved_answers = session.get("answers", {}).get(node_id, [])
    selected_items = saved_answers if isinstance(saved_answers, list) else []

    kb = build_node_keyboard(
        node=node,
        buttons=buttons,
        selected_items=selected_items,
        is_admin=is_admin,
        is_client_preview=is_client_preview
    )
    text_to_show = node.get("text", "Главное меню")

    if callback and callback.message:
        try:
            await callback.message.edit_text(text=text_to_show, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
            return
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            try:
                await callback.message.edit_text(text=text_to_show, reply_markup=kb, parse_mode=None, disable_web_page_preview=True)
                return
            except Exception:
                pass

    target_chat_id = message.chat.id if message else user_id
    try:
        await bot.send_message(chat_id=target_chat_id, text=text_to_show, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
    except TelegramBadRequest:
        await bot.send_message(chat_id=target_chat_id, text=text_to_show, reply_markup=kb, parse_mode=None, disable_web_page_preview=True)

# ----------------- 1. КОМАНДЫ -----------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await add_or_update_user(tg_id=user_id, username=username, full_name=message.from_user.full_name)

    perms = await get_user_permissions(user_id, username)
    is_staff_or_owner = bool(perms.get("is_owner") or perms.get("is_staff"))

    if is_staff_or_owner:
        admin_commands = [
            BotCommand(command="start", description="Главное меню / Перезапуск"),
            BotCommand(command="admin", description="Панель управления"),
            BotCommand(command="contacts", description="Контакты агентства")
        ]
        try:
            await message.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user_id))
        except Exception:
            pass
    else:
        try:
            await message.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))
        except Exception:
            pass

    session = await get_or_create_session(user_id)
    has_accepted_privacy = bool(session.get("answers", {}).get("_privacy_accepted", False))
    await reset_session(user_id, keep_privacy=True)
    
    if has_accepted_privacy:
        await update_session_node(user_id, "main_menu", push_history=False)
        await render_node(message.bot, user_id, node_id="main_menu", message=message)
    else:
        await update_session_node(user_id, "privacy_block", push_history=False)
        await render_node(message.bot, user_id, node_id="privacy_block", message=message)

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    await update_session_node(user_id, "main_menu", push_history=False)
    await message.answer("🚫 <i>Действие отменено. Возврат в главное меню.</i>", parse_mode="HTML")
    await render_node(message.bot, user_id, node_id="main_menu", message=message)

@router.message(Command("contacts"))
async def cmd_contacts(message: Message):
    await render_node(message.bot, message.from_user.id, node_id="contacts_screen", message=message)

@router.message(Command("admin"))
async def redirect_to_admin(message: Message, state: FSMContext):
    from handlers.admin_cms import cmd_admin_panel
    await cmd_admin_panel(message, state)

# ----------------- 2. КНОПКИ НАВИГАЦИИ -----------------

@router.callback_query(F.data.startswith("btn:"))
async def process_button_click(callback: CallbackQuery):
    await callback.answer()
    btn_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    from database.db import DB_NAME
    import aiosqlite
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM buttons WHERE id = ?", (btn_id,)) as cursor:
            btn_row = await cursor.fetchone()

    if not btn_row:
        return

    btn = dict(btn_row)
    action = btn.get("action_type", "navigate")
    target_node = btn.get("target_node_id", "")
    btn_text = btn.get("text", "")
    budget_weight = btn.get("budget_weight", 0.0)
    timeline_days = btn.get("timeline_days", 0)

    session = await get_or_create_session(user_id)

    if session.get("current_node_id") == "privacy_block" or (action == "navigate" and target_node == "main_menu"):
        await save_session_answer(user_id, "_privacy_accepted", True)

    if action == "back":
        prev_node = await pop_session_history(user_id)
        if prev_node in ("final_lead_name", "final_lead_phone"):
            profile = await get_user_profile(user_id)
            if profile and profile.get("phone") and profile.get("saved_name"):
                prev_node = await pop_session_history(user_id)
        await render_node(callback.bot, user_id, prev_node, callback=callback)
        return

    if action == "navigate" and target_node:
        current_node_id = session.get("current_node_id")
        answers = session.get("answers", {})
        answers[current_node_id] = btn_text
        answers["_calc_budget"] = answers.get("_calc_budget", 0.0) + budget_weight
        answers["_calc_days"] = answers.get("_calc_days", 0) + timeline_days
        
        await save_session_answer(user_id, current_node_id, btn_text)
        await save_session_answer(user_id, "_calc_budget", answers["_calc_budget"])
        await save_session_answer(user_id, "_calc_days", answers["_calc_days"])

        await update_session_node(user_id, target_node, push_history=True)
        await render_node(callback.bot, user_id, target_node, callback=callback)
        return

    # Предпросмотр для администратора / отправка для клиента
    if action == "action" and target_node.startswith("submit_lead:"):
        perms = await get_user_permissions(user_id)
        preferred_time = target_node.split(":")[1]
        await save_session_answer(user_id, "preferred_time", preferred_time)

        if perms.get("is_owner") or perms.get("can_content"):
            from services.lead_service import calculate_project_estimate
            est_b, est_t = await calculate_project_estimate(session)
            preview_txt = (
                "👁 <b>[ПРЕДПРОСМОТР ВЛАДЕЛЬЦА]</b>\n\n"
                "Финальный расчет сметы для клиента:\n"
                f"• Бюджет: <b>{est_b}</b>\n• Сроки: <b>{est_t}</b>\n\n"
                "<i>(Заявка в чат менеджеров не отправлялась, так как вы в режиме администратора).</i>"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 В главное меню", callback_data="btn_nav_main")],
                [InlineKeyboardButton(text="🛠 В панель управления", callback_data="adm_back_dash")]
            ])
            await callback.message.edit_text(preview_txt, reply_markup=kb, parse_mode="HTML")
            return

        from services.lead_service import finalize_lead_submission
        await finalize_lead_submission(callback.bot, user_id, callback=callback)
        return

# ----------------- 3. ЧЕКБОКСЫ -----------------

@router.callback_query(F.data.startswith("tog:"))
async def process_toggle_checkbox(callback: CallbackQuery):
    btn_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    from database.db import DB_NAME
    import aiosqlite
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM buttons WHERE id = ?", (btn_id,)) as cursor:
            btn_row = await cursor.fetchone()

    if not btn_row:
        await callback.answer()
        return

    btn = dict(btn_row)
    btn_text = btn.get("text", "")
    session = await get_or_create_session(user_id)
    current_node_id = session["current_node_id"]

    selected = await toggle_multiselect_option(user_id, current_node_id, btn_text)
    await callback.answer()

    node = await get_node(current_node_id)
    buttons = await get_node_buttons(current_node_id)
    perms = await get_user_permissions(user_id, callback.from_user.username or "")
    is_admin = bool(perms.get("can_content") or perms.get("is_owner"))

    kb = build_node_keyboard(node=node, buttons=buttons, selected_items=selected, is_admin=is_admin)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except TelegramBadRequest:
        pass

@router.callback_query(F.data == "multi_done")
async def process_multiselect_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    session = await get_or_create_session(user_id)
    current_node_id = session["current_node_id"]
    current_node = await get_node(current_node_id)
    selected_items = session.get("answers", {}).get(current_node_id, [])

    if not selected_items:
        await callback.answer("⚠️ Выберите хотя бы один вариант, чтобы продолжить!", show_alert=True)
        return

    await callback.answer()
    if not current_node:
        return

    buttons = await get_node_buttons(current_node_id)
    add_budget = sum(b.get("budget_weight", 0.0) for b in buttons if b["text"] in selected_items)
    add_days = sum(b.get("timeline_days", 0) for b in buttons if b["text"] in selected_items)

    answers = session.get("answers", {})
    await save_session_answer(user_id, "_calc_budget", answers.get("_calc_budget", 0.0) + add_budget)
    await save_session_answer(user_id, "_calc_days", answers.get("_calc_days", 0) + add_days)

    next_node = current_node.get("next_node_id") or "main_menu"
    await update_session_node(user_id, next_node, push_history=True)
    await render_node(callback.bot, user_id, next_node, callback=callback)

@router.callback_query(F.data == "btn_back")
async def process_generic_back(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    prev_node = await pop_session_history(user_id)
    if prev_node in ("final_lead_name", "final_lead_phone"):
        profile = await get_user_profile(user_id)
        if profile and profile.get("phone") and profile.get("saved_name"):
            prev_node = await pop_session_history(user_id)
    await render_node(callback.bot, user_id, prev_node, callback=callback)

# ----------------- 4. ВАЛИДАЦИЯ ВВОДА ТЕКСТА -----------------

@router.message(StateFilter(None), F.text)
async def process_text_inputs(message: Message):
    user_id = message.from_user.id
    session = await get_or_create_session(user_id)
    node = await get_node(session.get("current_node_id", ""))
    if not node or node.get("node_type") != "input_text":
        return

    entered_text = message.text.strip()
    node_id = node["id"]

    # Валидация телефона
    if node_id == "final_lead_phone":
        digits_only = re.sub(r"\D", "", entered_text)
        if not PHONE_REGEX.match(entered_text) or len(digits_only) < 10:
            await message.answer(
                "⚠️ <b>Некорректный номер телефона!</b>\n"
                "Пожалуйста, введите номер в формате: <code>+7 999 123-45-67</code> или <code>89991234567</code>",
                parse_mode="HTML"
            )
            return
        answers = session.get("answers", {})
        name = answers.get("final_lead_name", message.from_user.first_name or "Клиент")
        await save_user_profile(user_id, saved_name=name, phone=entered_text)

    # Валидация ссылки
    if node_id in ("promo_url_input", "fix_url_input", "input_examples_link"):
        if not is_valid_link(entered_text):
            await message.answer(
                "⚠️ <b>Указана некорректная ссылка!</b>\n"
                "Пожалуйста, отправьте реальный адрес сайта (например: <code>mysite.ru</code>, <code>https://mysite.ru</code> или <code>@username</code>):",
                parse_mode="HTML"
            )
            return

    await save_session_answer(user_id, node_id, entered_text)
    next_node = node.get("next_node_id") or "main_menu"
    await update_session_node(user_id, next_node, push_history=True)
    await render_node(message.bot, user_id, next_node, message=message)

@router.message(StateFilter(None), F.document)
async def process_file_input(message: Message):
    user_id = message.from_user.id
    session = await get_or_create_session(user_id)
    node = await get_node(session.get("current_node_id", ""))
    if not node or node.get("node_type") != "input_file":
        return

    file_id = message.document.file_id
    file_name = message.document.file_name or "Документ ТЗ"
    await save_session_answer(user_id, node["id"], f"Файл: {file_name}")
    await save_session_answer(user_id, "tz_file_id", file_id)

    await message.answer(f"📎 <b>Файл «{html.escape(file_name)}» успешно прикреплен!</b>", parse_mode="HTML")
    next_node = node.get("next_node_id") or "main_menu"
    await update_session_node(user_id, next_node, push_history=True)
    await render_node(message.bot, user_id, next_node, message=message)