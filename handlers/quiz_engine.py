import html
import re
import logging
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton,
    BotCommand, BotCommandScopeChat
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from database.queries import (
    get_node, get_node_buttons, get_button_by_id, get_or_create_session,
    update_session_node, pop_session_history, toggle_multiselect_option,
    save_session_answer, reset_session, get_user_permissions,
    get_user_profile, save_user_profile, add_or_update_user, get_setting
)
from keyboards.engine_kb import build_node_keyboard

router = Router()
logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r"^[\+]?[0-9\s\-\(\)]{10,18}$")

PROMO_CHANNEL_LINKS = [
    ("Сайт", "promo_link_site"),
    ("Соцсети", "promo_link_social"),
    ("Профиль в 2ГИС", "promo_link_2gis"),
    ("Яндекс Бизнес", "promo_link_yabiz"),
    ("Яндекс Карты", "promo_link_yamaps"),
    ("Яндекс Услуги", "promo_link_yaserv"),
]

PROMO_STATUS_FOLLOWUPS = [
    ("Да, через платную рекламу", "promo_current_paid_input"),
    ("Да, но не знаю точно, что это", "promo_current_unknown_input"),
    ("Продвигали раньше, но сейчас нет", "promo_current_past_input"),
]


async def safe_answer(callback: CallbackQuery, text: str = None, show_alert: bool = False):
    """Безопасный ответ на callback, чтобы сетевая задержка никогда не прерывала переход по меню."""
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except Exception:
        pass


def is_valid_link(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    pattern = re.compile(
        r"([a-zA-Z0-9а-яА-Я\-_]+\.[a-zA-Zа-яА-Я]{2,63})|(@[a-zA-Z0-9_]{3,32})|(https?://\S+)",
        re.IGNORECASE
    )
    return bool(pattern.search(t))


async def render_node(bot, user_id: int, node_id: str, message: Message = None, callback: CallbackQuery = None, force_client_view: bool = False):
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

    if node_id in ("final_lead_name", "final_lead_phone"):
        profile = await get_user_profile(user_id)
        if profile:
            if node_id == "final_lead_name" and profile.get("saved_name"):
                s_name = profile["saved_name"]
                kb.inline_keyboard.insert(0, [
                    InlineKeyboardButton(text=f"👤 Оставить имя: {s_name}", callback_data="autofill_name")
                ])
            elif node_id == "final_lead_phone" and profile.get("phone"):
                s_phone = profile["phone"]
                kb.inline_keyboard.insert(0, [
                    InlineKeyboardButton(text=f"📱 Оставить номер: {s_phone}", callback_data="autofill_phone")
                ])

    text_to_show = node.get("text", "Главное меню")

    if node_id == "contacts_screen":
        tg = await get_setting("agency_telegram", "@site_it")
        phone = await get_setting("agency_phone", "+7 999 155-10-43")
        email = await get_setting("agency_email", "site-it@mail.ru")
        text_to_show = re.sub(r"(Telegram:</b>\s*).*", rf"\g<1>{html.escape(tg)}", text_to_show)
        text_to_show = re.sub(r"(Телефон:</b>\s*).*", rf"\g<1>{html.escape(phone)}", text_to_show)
        text_to_show = re.sub(r"(Email:</b>\s*).*", rf"\g<1>{html.escape(email)}", text_to_show)

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
async def cmd_contacts(message: Message, state: FSMContext):
    await state.clear()
    await update_session_node(message.from_user.id, "contacts_screen", push_history=True)
    await render_node(message.bot, message.from_user.id, node_id="contacts_screen", message=message)


@router.message(Command("admin"))
async def redirect_to_admin(message: Message, state: FSMContext):
    from handlers.admin_cms import cmd_admin_panel
    await cmd_admin_panel(message, state)


# ----------------- 2. АВТОПОДСТАНОВКА ИМЕНИ И ТЕЛЕФОНА -----------------

@router.callback_query(F.data == "autofill_name")
async def handle_autofill_name(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(callback)
    user_id = callback.from_user.id
    profile = await get_user_profile(user_id)
    name = (profile or {}).get("saved_name") or callback.from_user.first_name or "Клиент"
    await save_session_answer(user_id, "final_lead_name", name)
    await update_session_node(user_id, "final_lead_phone", push_history=True)
    await render_node(callback.bot, user_id, "final_lead_phone", callback=callback)


@router.callback_query(F.data == "autofill_phone")
async def handle_autofill_phone(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(callback)
    user_id = callback.from_user.id
    profile = await get_user_profile(user_id)
    phone = (profile or {}).get("phone") or ""
    if phone:
        await save_session_answer(user_id, "final_lead_phone", phone)
        await update_session_node(user_id, "final_lead_messenger", push_history=True)
        await render_node(callback.bot, user_id, "final_lead_messenger", callback=callback)


# ----------------- 3. КНОПКИ НАВИГАЦИИ -----------------

@router.callback_query(F.data.startswith("btn:"))
async def process_button_click(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(callback)
    btn_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    btn = await get_button_by_id(btn_id)
    if not btn:
        return

    action = btn.get("action_type", "navigate")
    target_node = btn.get("target_node_id", "")
    btn_text = btn.get("text", "")
    budget_weight = float(btn.get("budget_weight", 0.0))
    timeline_days = int(btn.get("timeline_days", 0))

    session = await get_or_create_session(user_id)
    current_node_id = session.get("current_node_id", "main_menu")

    if current_node_id == "privacy_block" or (action == "navigate" and target_node == "main_menu"):
        await save_session_answer(user_id, "_privacy_accepted", True)

    if action == "back":
        await save_session_answer(user_id, "_step_queue", [])
        prev_node = await pop_session_history(user_id)
        await render_node(callback.bot, user_id, prev_node, callback=callback)
        return

    if action == "navigate" and target_node:
        if target_node == "main_menu":
            await reset_session(user_id, keep_privacy=True)
            await update_session_node(user_id, "main_menu", push_history=False)
            await render_node(callback.bot, user_id, "main_menu", callback=callback)
            return

        answers = session.get("answers", {})
        curr_node = await get_node(current_node_id)
        curr_type = curr_node.get("node_type", "regular") if curr_node else "regular"

        node_budgets = answers.get("_node_budgets", {})
        node_days = answers.get("_node_days", {})

        if curr_type == "multiselect":
            selected_items = answers.get(current_node_id, [])
            if isinstance(selected_items, list) and selected_items:
                all_btns = await get_node_buttons(current_node_id)
                node_budgets[current_node_id] = sum(float(b.get("budget_weight", 0.0)) for b in all_btns if b["text"] in selected_items)
                node_days[current_node_id] = sum(int(b.get("timeline_days", 0)) for b in all_btns if b["text"] in selected_items)
        else:
            skip_answer_nodes = {"main_menu", "privacy_block", "site_sections_category", "portfolio_spheres", "contacts_screen"}
            if current_node_id not in skip_answer_nodes:
                await save_session_answer(user_id, current_node_id, btn_text)
            node_budgets[current_node_id] = budget_weight
            node_days[current_node_id] = timeline_days

        await save_session_answer(user_id, "_node_budgets", node_budgets)
        await save_session_answer(user_id, "_node_days", node_days)

        if current_node_id == "design_style_page" and target_node == "design_examples_page":
            site_type = str(answers.get("new_site_type", ""))
            if "Товары и услуги" in site_type or "combo_priority" in answers:
                target_node = "combo_flows_page"

        await update_session_node(user_id, target_node, push_history=True)
        await render_node(callback.bot, user_id, target_node, callback=callback)
        return

    if action == "action" and target_node.startswith("submit_lead:"):
        preferred_time = target_node.split(":", 1)[1]
        await save_session_answer(user_id, "preferred_time", preferred_time)

        from services.lead_service import finalize_lead_submission
        await finalize_lead_submission(callback.bot, user_id, callback=callback)
        return


# ----------------- 4. ЧЕКБОКСЫ (МУЛЬТИВЫБОР) -----------------

@router.callback_query(F.data.startswith("tog:"))
async def process_toggle_checkbox(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    btn_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    btn = await get_button_by_id(btn_id)
    if not btn:
        await safe_answer(callback)
        return

    btn_text = btn.get("text", "")
    session = await get_or_create_session(user_id)
    current_node_id = session["current_node_id"]

    selected = await toggle_multiselect_option(user_id, current_node_id, btn_text)
    await safe_answer(callback)

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
async def process_multiselect_done(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    session = await get_or_create_session(user_id)
    current_node_id = session["current_node_id"]
    current_node = await get_node(current_node_id)
    answers = session.get("answers", {})
    selected_items = answers.get(current_node_id, [])

    if not selected_items:
        await safe_answer(callback, "⚠️ Выберите хотя бы один вариант, чтобы продолжить!", show_alert=True)
        return

    await safe_answer(callback)
    if not current_node:
        return

    buttons = await get_node_buttons(current_node_id)
    add_budget = sum(float(b.get("budget_weight", 0.0)) for b in buttons if b["text"] in selected_items)
    add_days = sum(int(b.get("timeline_days", 0)) for b in buttons if b["text"] in selected_items)

    node_budgets = answers.get("_node_budgets", {})
    node_days = answers.get("_node_days", {})
    node_budgets[current_node_id] = add_budget
    node_days[current_node_id] = add_days

    await save_session_answer(user_id, "_node_budgets", node_budgets)
    await save_session_answer(user_id, "_node_days", node_days)

    next_node = current_node.get("next_node_id") or "main_menu"

    if current_node_id == "promo_target":
        queue = [n_id for label, n_id in PROMO_CHANNEL_LINKS if label in selected_items]
        if queue:
            next_node = queue.pop(0)
            await save_session_answer(user_id, "_step_queue", queue)
        else:
            await save_session_answer(user_id, "_step_queue", [])

    elif current_node_id == "promo_current_status":
        is_never_or_unsure = any(
            ("Никогда не продвигали" in item or "Затрудняюсь ответить" in item)
            for item in selected_items
        )
        if is_never_or_unsure:
            await save_session_answer(user_id, "_step_queue", [])
            next_node = "final_lead_name"
        else:
            queue = [n_id for label, n_id in PROMO_STATUS_FOLLOWUPS if label in selected_items]
            if queue:
                queue.append("promo_helped_page")
                next_node = queue.pop(0)
                await save_session_answer(user_id, "_step_queue", queue)
            else:
                await save_session_answer(user_id, "_step_queue", [])
                next_node = "promo_helped_page"

    await update_session_node(user_id, next_node, push_history=True)
    await render_node(callback.bot, user_id, next_node, callback=callback)


@router.callback_query(F.data == "btn_back")
async def process_generic_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(callback)
    user_id = callback.from_user.id
    await save_session_answer(user_id, "_step_queue", [])
    prev_node = await pop_session_history(user_id)
    await render_node(callback.bot, user_id, prev_node, callback=callback)


# ----------------- 5. ВАЛИДАЦИЯ И ОБРАБОТКА ВВОДА ТЕКСТА И ФАЙЛОВ -----------------

@router.message(StateFilter(None), F.text)
async def process_text_inputs(message: Message):
    user_id = message.from_user.id
    session = await get_or_create_session(user_id)
    node = await get_node(session.get("current_node_id", ""))
    if not node or node.get("node_type") != "input_text":
        return

    entered_text = message.text.strip()
    node_id = node["id"]

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

    link_nodes = {
        "promo_url_input", "fix_url_input", "input_examples_link",
        "promo_link_site", "promo_link_social", "promo_link_2gis",
        "promo_link_yabiz", "promo_link_yamaps", "promo_link_yaserv"
    }
    if node_id in link_nodes:
        if not is_valid_link(entered_text):
            await message.answer(
                "⚠️ <b>Пожалуйста, укажите корректную ссылку или @username!</b>\n"
                "Например: <code>mysite.ru</code>, <code>https://mysite.ru</code> или <code>@username</code>:",
                parse_mode="HTML"
            )
            return

    await save_session_answer(user_id, node_id, entered_text)

    updated_session = await get_or_create_session(user_id)
    queue = updated_session.get("answers", {}).get("_step_queue", [])
    if isinstance(queue, list) and queue:
        next_node = queue.pop(0)
        await save_session_answer(user_id, "_step_queue", queue)
    else:
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
