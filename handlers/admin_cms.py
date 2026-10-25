import html
import io
import re
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import OWNER_ID
from database.queries import (
    get_node, get_node_buttons, update_node_text, add_button, delete_button,
    get_button_by_id, update_button_text, update_button_weights, update_button_target,
    move_button_to_position, swap_button_step,
    create_custom_node, delete_custom_node, get_all_nodes_list, export_scenario_json, import_scenario_json,
    get_setting, set_setting, get_all_users_by_target, get_all_leads,
    get_all_staff, get_staff_by_db_id, set_user_role_by_username,
    get_user_permissions, toggle_staff_permission, apply_staff_role_preset, add_or_update_user
)
from services.excel_service import generate_leads_excel
from scenario.loader import seed_scenario_to_db
from database.db import DB_NAME
import aiosqlite

router = Router()
logger = logging.getLogger(__name__)

URL_VALID_REGEX = re.compile(
    r"^(https?://)?[a-zA-Z0-9\-_]+(\.[a-zA-Z0-9\-_]+)+([/?].*)?$|^tg://[a-zA-Z0-9_/?=&]+$",
    re.IGNORECASE
)

def format_and_validate_url(text: str) -> str | None:
    t = text.strip()
    if not URL_VALID_REGEX.match(t):
        return None
    if not t.startswith(("http://", "https://", "tg://")):
        t = "https://" + t
    return t

class AdminCMSFSM(StatesGroup):
    waiting_for_new_text = State()
    waiting_for_btn_name = State()
    waiting_for_btn_action = State()
    waiting_for_btn_target = State()
    waiting_for_new_node_text = State()
    waiting_for_new_node_type = State()
    waiting_for_new_node_dest = State()
    waiting_for_btn_edit_text = State()
    waiting_for_btn_edit_url = State()
    waiting_for_btn_calc = State()
    waiting_for_btn_reorder = State()
    waiting_for_setting_value = State()
    waiting_for_broadcast = State()
    waiting_for_staff_user = State()
    waiting_for_backup_file = State()

def is_owner_filter(user_id: int) -> bool:
    return user_id == OWNER_ID

def build_dashboard_kb(perms: dict) -> InlineKeyboardMarkup:
    is_owner = perms.get("is_owner", False)
    kb = []
    if perms.get("can_export"):
        kb.append([InlineKeyboardButton(text="📥 Скачать базу лидов в Excel", callback_data="adm_export_excel")])

    row2 = []
    if perms.get("can_calc"):
        row2.append(InlineKeyboardButton(text="🧮 Настройка сметы", callback_data="adm_calc_rates"))
    if is_owner:
        row2.append(InlineKeyboardButton(text="👥 Персонал и роли", callback_data="adm_staff_menu"))
    if row2:
        kb.append(row2)

    row3 = []
    if is_owner:
        row3.append(InlineKeyboardButton(text="⚙️ Настройки агентства", callback_data="adm_agency_settings"))
    if perms.get("can_leads"):
        row3.append(InlineKeyboardButton(text="📊 Аналитика лидов", callback_data="adm_leads_stats"))
    if row3:
        kb.append(row3)

    row4 = []
    if perms.get("can_broadcast"):
        row4.append(InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast_start"))
    row4.append(InlineKeyboardButton(text="🌐 Перейти к боту (Редактор)", callback_data="adm_jump_bot"))
    kb.append(row4)

    if is_owner:
        kb.append([
            InlineKeyboardButton(text="💾 Скачать бэкап (JSON)", callback_data="adm_backup_json"),
            InlineKeyboardButton(text="📥 Восстановить из JSON", callback_data="adm_restore_json_start")
        ])
        kb.append([InlineKeyboardButton(text="🔄 Сброс к заводским", callback_data="adm_reset_confirm")])

    kb.append([InlineKeyboardButton(text="❌ Закрыть панель", callback_data="adm_close")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_staff_permissions_kb(staff_user: dict) -> InlineKeyboardMarkup:
    u_id = staff_user["id"]
    c_leads = "✅" if staff_user.get("can_leads", 1) else "⬜"
    c_export = "✅" if staff_user.get("can_export", 1) else "⬜"
    c_calc = "✅" if staff_user.get("can_calc", 0) else "⬜"
    c_content = "✅" if staff_user.get("can_content", 0) else "⬜"
    c_bcast = "✅" if staff_user.get("can_broadcast", 0) else "⬜"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨‍💼 Менеджер", callback_data=f"adm_preset:{u_id}:sales"),
            InlineKeyboardButton(text="✍️ Редактор", callback_data=f"adm_preset:{u_id}:editor")
        ],
        [
            InlineKeyboardButton(text="🧮 Сметчик", callback_data=f"adm_preset:{u_id}:estimator"),
            InlineKeyboardButton(text="👑 Управляющий", callback_data=f"adm_preset:{u_id}:super")
        ],
        [InlineKeyboardButton(text=f"{c_leads} Доступ к заявкам и CRM", callback_data=f"adm_tperm:{u_id}:can_leads")],
        [InlineKeyboardButton(text=f"{c_export} Выгрузка базы в Excel", callback_data=f"adm_tperm:{u_id}:can_export")],
        [InlineKeyboardButton(text=f"{c_calc} Настройка цен и сроков сметы", callback_data=f"adm_tperm:{u_id}:can_calc")],
        [InlineKeyboardButton(text=f"{c_content} Редактор экранов и кнопок (CMS)", callback_data=f"adm_tperm:{u_id}:can_content")],
        [InlineKeyboardButton(text=f"{c_bcast} Массовая рассылка клиентам", callback_data=f"adm_tperm:{u_id}:can_broadcast")],
        [InlineKeyboardButton(text="🗑 Снять все права администратора", callback_data=f"adm_rev_st_id:{u_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к списку персонала", callback_data="adm_staff_menu")]
    ])

# ----------------- 0. АВТОПРИВЯЗКА ГРУППЫ -----------------

@router.message(Command("set_leads_chat"))
async def cmd_bind_leads_chat(message: Message):
    if not is_owner_filter(message.from_user.id):
        await message.answer("⛔ Только владелец бота может привязать этот чат.")
        return
    if message.chat.type in ("group", "supergroup"):
        chat_id_str = str(message.chat.id)
        chat_title = message.chat.title or "Рабочая группа"
        await set_setting("leads_channel_id", chat_id_str)
        await set_setting("leads_channel_title", chat_title)
        await message.answer(f"🎉 <b>Группа привязана!</b>\n• Название: <b>{html.escape(chat_title)}</b>\n• ID: <code>{chat_id_str}</code>", parse_mode="HTML")
    else:
        await message.answer("⚠️ Отправьте эту команду внутри группы отдела продаж!")

# ----------------- 1. ВХОД В ПАНЕЛЬ (/admin) -----------------

@router.message(Command("admin"))
async def cmd_admin_panel(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await add_or_update_user(user_id, username, message.from_user.full_name or "")
    perms = await get_user_permissions(user_id, username)
    
    if not perms.get("is_owner") and not perms.get("is_staff"):
        await message.answer("⛔ У вас нет доступа к панели управления.")
        return
        
    await state.clear()
    role_title = perms.get("role_title", "Администратор")
    await message.answer(
        f"🛠 <b>ПАНЕЛЬ УПРАВЛЕНИЯ</b>\n👤 Ваша роль: <b>{html.escape(role_title)}</b>\n\nВыберите раздел:",
        reply_markup=build_dashboard_kb(perms),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_back_dash")
async def back_to_dash(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("is_owner") and not perms.get("is_staff"):
        return
    await state.clear()
    role_title = perms.get("role_title", "Администратор")
    await callback.message.edit_text(
        f"🛠 <b>ПАНЕЛЬ УПРАВЛЕНИЯ</b>\n👤 Ваша роль: <b>{html.escape(role_title)}</b>",
        reply_markup=build_dashboard_kb(perms),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_close")
async def close_dash(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

@router.callback_query(F.data == "adm_jump_bot")
async def jump_to_client_bot(callback: CallbackQuery):
    await callback.answer()
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, "main_menu", callback=callback)

# ----------------- 2. ПРЕДПРОСМОТР, СКАЧИВАНИЕ И ВОССТАНОВЛЕНИЕ БЭКАПА -----------------

@router.callback_query(F.data.startswith("adm_client_view:"))
async def preview_as_client(callback: CallbackQuery):
    await callback.answer("Режим: Глазами клиента")
    node_id = callback.data.split(":")[1]
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, node_id, callback=callback, force_client_view=True)

@router.callback_query(F.data == "adm_backup_json")
async def backup_json_handler(callback: CallbackQuery):
    if not is_owner_filter(callback.from_user.id):
        await callback.answer("Только для Владельца!", show_alert=True)
        return
    await callback.answer("Создаю бэкап...")
    json_str = await export_scenario_json()
    doc = BufferedInputFile(json_str.encode("utf-8"), filename="scenario_backup.json")
    await callback.message.answer_document(document=doc, caption="💾 <b>Резервная копия сценария (JSON)</b>", parse_mode="HTML")

# Восстановление из бэкапа JSON
@router.callback_query(F.data == "adm_restore_json_start")
async def restore_json_start(callback: CallbackQuery, state: FSMContext):
    if not is_owner_filter(callback.from_user.id):
        await callback.answer("Только для Владельца!", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminCMSFSM.waiting_for_backup_file)
    await callback.message.edit_text(
        "📥 <b>Восстановление сценария из файла JSON</b>\n\n"
        "Отправьте ранее сохраненный файл <code>scenario_backup.json</code> документом в этот чат:\n\n"
        "⚠️ <i>Все экраны и кнопки будут заменены версией из файла. База заявок и клиентов не удаляется!</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_back_dash")]]),
        parse_mode="HTML"
    )

@router.message(AdminCMSFSM.waiting_for_backup_file, F.document)
async def process_backup_file_upload(message: Message, state: FSMContext):
    doc = message.document
    if not (doc.file_name or "").lower().endswith(".json"):
        await message.answer("⚠️ Файл должен иметь расширение <code>.json</code>! Отправьте корректный файл бэкапа:", parse_mode="HTML")
        return

    file_io = io.BytesIO()
    await message.bot.download(doc, destination=file_io)
    json_str = file_io.getvalue().decode("utf-8")

    ok, res_msg = await import_scenario_json(json_str)
    await state.clear()

    if ok:
        await message.answer(
            f"🎉 <b>{res_msg}</b>\nСценарий успешно восстановлен из загруженного файла!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 В панель управления", callback_data="adm_back_dash")]]),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"❌ <b>Ошибка восстановления:</b>\n{res_msg}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 В панель управления", callback_data="adm_back_dash")]]),
            parse_mode="HTML"
        )

# ----------------- 3. КОНСТРУКТОР ЭКРАНОВ И КНОПОК -----------------

@router.callback_query(F.data.startswith("adm_add_btn:"))
async def add_btn_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_content"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    node_id = callback.data.split(":")[1]
    curr_node = await get_node(node_id)
    
    await state.update_data(target_node_id=node_id, current_node_type=curr_node.get("node_type", "regular") if curr_node else "regular")
    await state.set_state(AdminCMSFSM.waiting_for_btn_name)

    if curr_node and curr_node.get("node_type") == "multiselect":
        prompt = f"➕ <b>Добавление варианта ответа (чекбокса) на экран:</b> <code>{node_id}</code>\n\nНапишите название пункта (например: <i>Минимализм</i>):"
    else:
        prompt = f"➕ <b>Добавление кнопки на экран:</b> <code>{node_id}</code>\n\nНапишите название кнопки (например: <i>🔥 Портфолио за 2026 год</i>):"

    await callback.message.answer(
        prompt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel_edit")]]),
        parse_mode="HTML"
    )

@router.message(AdminCMSFSM.waiting_for_btn_name)
async def process_btn_name(message: Message, state: FSMContext):
    data = await state.get_data()
    btn_name = message.text.strip()
    curr_type = data.get("current_node_type", "regular")
    node_id = data.get("target_node_id")

    # Для мультивыбора кнопка сразу создается как чекбокс toggle!
    if curr_type == "multiselect":
        await add_button(node_id=node_id, text=btn_name, action_type="toggle", target_node_id="", url="")
        await state.clear()
        await message.answer(
            f"✅ <b>Чекбокс «{html.escape(btn_name)}» успешно добавлен!</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁 Посмотреть экран", callback_data=f"adm_preview_node:{node_id}")]]) ,
            parse_mode="HTML"
        )
        return

    await state.update_data(btn_name=btn_name)
    await state.set_state(AdminCMSFSM.waiting_for_btn_action)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Создать НОВЫЙ экран под эту кнопку", callback_data="btn_act_create_node")],
        [InlineKeyboardButton(text="➡️ Переход на существующий экран (список)", callback_data="btn_act_pick_node")],
        [InlineKeyboardButton(text="🔗 Внешняя ссылка (URL сайт/канал)", callback_data="btn_act_url")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel_edit")]
    ])
    await message.answer("Шаг 2: Что должна делать эта кнопка при нажатии?", reply_markup=kb)

@router.callback_query(F.data == "btn_act_create_node", AdminCMSFSM.waiting_for_btn_action)
async def btn_create_new_node_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminCMSFSM.waiting_for_new_node_text)
    await callback.message.edit_text(
        "🆕 <b>Создание нового экрана</b>\n\n"
        "Напишите текст/вопрос для экрана\n"
        "<i>(например: «Укажите ваш ИНН для договора:» или «Какой стиль сайта вам ближе?:»)</i>:",
        parse_mode="HTML"
    )

@router.message(AdminCMSFSM.waiting_for_new_node_text)
async def process_new_node_text_creation(message: Message, state: FSMContext):
    await state.update_data(new_node_text=message.text.strip())
    await state.set_state(AdminCMSFSM.waiting_for_new_node_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Обычный экран с кнопками-переходами", callback_data="nntype:regular")],
        [InlineKeyboardButton(text="☑️ Экран с галочками (Мультивыбор)", callback_data="nntype:multiselect")],
        [InlineKeyboardButton(text="✍️ Экран с вводом текста от клиента", callback_data="nntype:input_text")]
    ])
    await message.answer("Шаг 3: Выберите тип поведения нового экрана:", reply_markup=kb)

@router.callback_query(F.data.startswith("nntype:"), AdminCMSFSM.waiting_for_new_node_type)
async def process_new_node_type_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    n_type = callback.data.split(":")[1]
    await state.update_data(new_node_type=n_type)

    if n_type in ("input_text", "multiselect"):
        await state.set_state(AdminCMSFSM.waiting_for_new_node_dest)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏁 Сразу к сбору контактов (финал)", callback_data="dest:final_lead_name")],
            [InlineKeyboardButton(text="🏠 В Главное меню", callback_data="dest:main_menu")],
            [InlineKeyboardButton(text="⬅️ На исходный экран", callback_data="dest:parent")]
        ])
        await callback.message.edit_text("Шаг 4: Куда переводить клиента после того, как он ответит на этот вопрос?", reply_markup=kb)
    else:
        await finalize_node_creation(callback, state, next_dest="")

@router.callback_query(F.data.startswith("dest:"), AdminCMSFSM.waiting_for_new_node_dest)
async def process_new_node_dest_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    dest_code = callback.data.split(":")[1]
    data = await state.get_data()
    parent_id = data.get("target_node_id")
    final_dest = parent_id if dest_code == "parent" else dest_code
    await finalize_node_creation(callback, state, next_dest=final_dest)

async def finalize_node_creation(callback: CallbackQuery, state: FSMContext, next_dest: str):
    data = await state.get_data()
    parent_node_id = data.get("target_node_id")
    btn_name = data.get("btn_name")
    new_node_text = data.get("new_node_text")
    n_type = data.get("new_node_type", "regular")
    target_next = next_dest or parent_node_id

    created_node_id = await create_custom_node(text=new_node_text, node_type=n_type, next_node_id=target_next)
    await add_button(node_id=parent_node_id, text=btn_name, action_type="navigate", target_node_id=created_node_id)
    await state.clear()

    await callback.message.edit_text(
        f"🎉 <b>Новый экран успешно создан и привязан!</b>\n\n"
        f"• Кнопка перехода: <b>«{html.escape(btn_name)}»</b>\n"
        f"• Куда ведет после ответа: <code>{target_next}</code>\n\n"
        "⚡️ <i>Все ответы клиента на этом экране будут автоматически добавляться в итоговый бриф менеджерам!</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Открыть созданный экран", callback_data=f"adm_preview_node:{created_node_id}")],
            [InlineKeyboardButton(text="⬅️ Вернуться назад", callback_data=f"adm_preview_node:{parent_node_id}")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "btn_act_pick_node", AdminCMSFSM.waiting_for_btn_action)
async def btn_pick_existing_node(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    nodes = await get_all_nodes_list()
    kb = []
    for n in nodes[:25]:
        clean_preview = n["text"].replace("<b>", "").replace("</b>", "")[:20]
        kb.append([InlineKeyboardButton(text=f"📄 {n['id']} ({clean_preview}...)", callback_data=f"pick_target:{n['id']}")])
    kb.append([InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel_edit")])
    await callback.message.edit_text("Выберите экран для перехода:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data.startswith("pick_target:"))
async def process_picked_node_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    target_node = callback.data.split(":")[1]
    data = await state.get_data()
    parent_node = data.get("target_node_id")
    btn_name = data.get("btn_name")
    await add_button(node_id=parent_node, text=btn_name, action_type="navigate", target_node_id=target_node)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Кнопка «<b>{html.escape(btn_name)}</b>» теперь ведет на экран <code>{target_node}</code>!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁 Посмотреть", callback_data=f"adm_preview_node:{parent_node}")]]) ,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "btn_act_url", AdminCMSFSM.waiting_for_btn_action)
async def btn_action_url_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(btn_action_type="url")
    await state.set_state(AdminCMSFSM.waiting_for_btn_target)
    await callback.message.edit_text("Отправьте полную ссылку на сайт (например: <code>https://mysite.ru</code>):", parse_mode="HTML")

@router.message(AdminCMSFSM.waiting_for_btn_target)
async def process_btn_target(message: Message, state: FSMContext):
    valid_url = format_and_validate_url(message.text)
    if not valid_url:
        await message.answer("⚠️ <b>Некорректная ссылка!</b> Введите адрес с доменом (например: <code>mysite.ru</code>):", parse_mode="HTML")
        return

    data = await state.get_data()
    await add_button(node_id=data.get("target_node_id"), text=data.get("btn_name"), action_type="url", url=valid_url)
    await state.clear()
    await message.answer(
        f"🎉 <b>Кнопка-ссылка «{html.escape(data.get('btn_name'))}» добавлена!</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁 Посмотреть", callback_data=f"adm_preview_node:{data.get('target_node_id')}")]]) ,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_del_node:"))
async def delete_node_prompt(callback: CallbackQuery):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_content"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    node_id = callback.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Да, удалить экран", callback_data=f"adm_del_node_exec:{node_id}")],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data=f"adm_preview_node:{node_id}")]
    ])
    await callback.message.edit_text(f"⚠️ Удалить экран <code>{node_id}</code> и все ведущие на него кнопки?", reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_del_node_exec:"))
async def delete_node_execute(callback: CallbackQuery):
    node_id = callback.data.split(":")[1]
    ok, msg = await delete_custom_node(node_id)
    await callback.answer(msg, show_alert=True)
    if ok:
        from handlers.quiz_engine import render_node
        await render_node(callback.bot, callback.from_user.id, "main_menu", callback=callback)

# ----------------- 4. НАСТРОЙКА КНОПОК И ССЫЛОК -----------------

@router.callback_query(F.data.startswith("adm_list_btns:"))
async def list_node_buttons(callback: CallbackQuery):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_content"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    node_id = callback.data.split(":")[1]
    buttons = await get_node_buttons(node_id)
    content_btns = [b for b in buttons if b.get("action_type") != "back"]
    if not content_btns:
        await callback.answer("На этом экране нет настраиваемых кнопок.", show_alert=True)
        return
        
    kb = []
    for pos, b in enumerate(content_btns, start=1):
        btn_title = f"{pos}. {b['text'][:22]}"
        kb.append([InlineKeyboardButton(text=f"⚙️ {btn_title}", callback_data=f"adm_btn_opt:{b['id']}:{node_id}")])
        
    kb.append([InlineKeyboardButton(text="⬅️ Назад к экрану", callback_data=f"adm_preview_node:{node_id}")])
    await callback.message.edit_text(f"⚙️ <b>Кнопки экрана:</b> <code>{node_id}</code>\nВыберите кнопку:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_btn_opt:"))
async def button_options_card(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    btn = await get_button_by_id(btn_id)
    if not btn:
        return

    buttons = await get_node_buttons(node_id)
    content_btns = [b for b in buttons if b.get("action_type") != "back"]
    cur_pos = next((i + 1 for i, b in enumerate(content_btns) if b["id"] == btn_id), 1)
    total_pos = len(content_btns)

    target_info = btn.get('url') if btn.get('action_type') == 'url' else btn.get('target_node_id')
    text = (
        f"🔘 <b>НАСТРОЙКА КНОПКИ #{btn_id}</b>\n\n"
        f"• Текст: <b>{html.escape(btn['text'])}</b>\n"
        f"• Позиция в меню: <b>{cur_pos} из {total_pos}</b>\n"
        f"• Тип: <code>{btn['action_type']}</code>\n"
        f"• Ведет на: <code>{html.escape(str(target_info or 'Назад'))}</code>\n\nВыберите действие:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬆️ Выше", callback_data=f"adm_b_up:{btn_id}:{node_id}"),
            InlineKeyboardButton(text="⬇️ Ниже", callback_data=f"adm_b_down:{btn_id}:{node_id}")
        ],
        [InlineKeyboardButton(text="🔢 Задать номер позиции", callback_data=f"adm_b_pos:{btn_id}:{node_id}")],
        [InlineKeyboardButton(text="✏️ Изменить название кнопки", callback_data=f"adm_ebt:{btn_id}:{node_id}")],
        [InlineKeyboardButton(text="🔗 Изменить ссылку (URL)", callback_data=f"adm_eburl:{btn_id}:{node_id}")],
        [InlineKeyboardButton(text="🗑 Удалить эту кнопку", callback_data=f"adm_dbt:{btn_id}:{node_id}")],
        [InlineKeyboardButton(text="⬅️ К списку кнопок", callback_data=f"adm_list_btns:{node_id}")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_b_up:"))
async def move_btn_up_handler(callback: CallbackQuery):
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    await swap_button_step(btn_id, "up")
    await callback.answer("Перемещено выше!")
    await button_options_card(callback)

@router.callback_query(F.data.startswith("adm_b_down:"))
async def move_btn_down_handler(callback: CallbackQuery):
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    await swap_button_step(btn_id, "down")
    await callback.answer("Перемещено ниже!")
    await button_options_card(callback)

@router.callback_query(F.data.startswith("adm_b_pos:"))
async def move_btn_exact_pos_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    buttons = await get_node_buttons(node_id)
    content_btns = [b for b in buttons if b.get("action_type") != "back"]
    total = len(content_btns)

    await state.update_data(reorder_btn_id=btn_id, reorder_node_id=node_id, total_btns=total)
    await state.set_state(AdminCMSFSM.waiting_for_btn_reorder)

    await callback.message.edit_text(
        f"🔢 <b>Перемещение кнопки на нужную позицию</b>\n\n"
        f"Всего кнопок: <b>{total}</b>.\n"
        f"Отправьте номер новой позиции (от 1 до {total}):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"adm_btn_opt:{btn_id}:{node_id}")]]),
        parse_mode="HTML"
    )

@router.message(AdminCMSFSM.waiting_for_btn_reorder)
async def process_btn_reorder_input(message: Message, state: FSMContext):
    txt = message.text.strip()
    data = await state.get_data()
    btn_id = data.get("reorder_btn_id")
    node_id = data.get("reorder_node_id")
    total = data.get("total_btns", 1)

    if not txt.isdigit() or not (1 <= int(txt) <= total):
        await message.answer(f"⚠️ Введите число от 1 до {total}:")
        return

    ok, old_p, new_p = await move_button_to_position(btn_id, int(txt))
    await state.clear()
    await message.answer(
        f"✅ Кнопка перемещена с {old_p}-го на <b>{new_p}-е место</b>!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👁 Посмотреть экран", callback_data=f"adm_preview_node:{node_id}")],
            [InlineKeyboardButton(text="⚙️ К списку кнопок", callback_data=f"adm_list_btns:{node_id}")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_eburl:"))
async def edit_btn_url_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    await state.update_data(editing_btn_id=btn_id, parent_node_id=node_id)
    await state.set_state(AdminCMSFSM.waiting_for_btn_edit_url)
    await callback.message.edit_text("Отправьте новую ссылку для этой кнопки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"adm_btn_opt:{btn_id}:{node_id}")]]))

@router.message(AdminCMSFSM.waiting_for_btn_edit_url)
async def process_btn_new_url(message: Message, state: FSMContext):
    valid_url = format_and_validate_url(message.text)
    if not valid_url:
        await message.answer("⚠️ Некорректная ссылка! Введите адрес с доменом:", parse_mode="HTML")
        return
    data = await state.get_data()
    btn_id, node_id = data.get("editing_btn_id"), data.get("parent_node_id")
    await update_button_target(btn_id, "url", valid_url)
    await state.clear()
    await message.answer(f"✅ Ссылка обновлена!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁 Посмотреть", callback_data=f"adm_preview_node:{node_id}")]]) , parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_ebt:"))
async def edit_btn_text_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    await state.update_data(editing_btn_id=btn_id, parent_node_id=node_id)
    await state.set_state(AdminCMSFSM.waiting_for_btn_edit_text)
    await callback.message.edit_text("Отправьте новый текст для этой кнопки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"adm_btn_opt:{btn_id}:{node_id}")]]))

@router.message(AdminCMSFSM.waiting_for_btn_edit_text)
async def process_btn_new_text(message: Message, state: FSMContext):
    data = await state.get_data()
    btn_id, node_id = data.get("editing_btn_id"), data.get("parent_node_id")
    new_txt = message.text.strip()
    await update_button_text(btn_id, new_txt)
    await state.clear()
    await message.answer(f"✅ Текст кнопки изменен на: «{html.escape(new_txt)}»", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Посмотреть экран", callback_data=f"adm_preview_node:{node_id}")],
        [InlineKeyboardButton(text="⚙️ Кнопки", callback_data=f"adm_list_btns:{node_id}")]
    ]), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_dbt:"))
async def process_delete_btn_confirmed(callback: CallbackQuery):
    parts = callback.data.split(":")
    btn_id, node_id = int(parts[1]), parts[2]
    await delete_button(btn_id)
    await callback.answer("Кнопка удалена!")
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, node_id, callback=callback)

@router.callback_query(F.data.startswith("adm_edit_txt:"))
async def edit_node_text_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_content"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    node_id = callback.data.split(":")[1]
    node = await get_node(node_id)
    await state.update_data(editing_node_id=node_id)
    await state.set_state(AdminCMSFSM.waiting_for_new_text)
    await callback.message.answer(f"✏️ <b>Редактирование экрана:</b> <code>{node_id}</code>\n\nТекущий текст:\n<blockquote>{html.escape(node['text'])}</blockquote>\n\nОтправьте новый текст:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel_edit")]]), parse_mode="HTML")

@router.callback_query(F.data == "adm_cancel_edit")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Действие отменено.")

@router.message(AdminCMSFSM.waiting_for_new_text)
async def process_new_node_text(message: Message, state: FSMContext):
    data = await state.get_data()
    node_id = data.get("editing_node_id")
    await update_node_text(node_id, message.text.strip())
    await state.clear()
    await message.answer(f"✅ <b>Текст экрана '{node_id}' обновлен!</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Посмотреть (Редактор)", callback_data=f"adm_preview_node:{node_id}")],
        [InlineKeyboardButton(text="👁 Глазами клиента", callback_data=f"adm_client_view:{node_id}")]
    ]), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_preview_node:"))
async def preview_node(callback: CallbackQuery):
    await callback.answer()
    node_id = callback.data.split(":")[1]
    from handlers.quiz_engine import render_node
    await render_node(callback.bot, callback.from_user.id, node_id, callback=callback)

# ----------------- 5. ПЕРСОНАЛ, СМЕТА, ЭКСПОРТ И НАСТРОЙКИ -----------------

@router.callback_query(F.data == "adm_staff_menu")
async def staff_menu_handler(callback: CallbackQuery):
    await callback.answer()
    if not is_owner_filter(callback.from_user.id):
        await callback.answer("Только для Владельца!", show_alert=True)
        return
    staff = await get_all_staff()
    lines = ["👥 <b>УПРАВЛЕНИЕ АДМИНИСТРАТОРАМИ И РОЛЯМИ:</b>\n"]
    kb = []
    for s in staff:
        un = s.get('username')
        tag = f"@{un}" if un else f"ID: {s.get('tg_id')}"
        is_own = (s.get("role") == "owner" or s.get("tg_id") == OWNER_ID)
        r_title = "👑 ВЛАДЕЛЕЦ" if is_own else f"👨‍💼 {s.get('role_title') or 'Менеджер'}"
        lines.append(f"• {tag} — <b>{html.escape(r_title)}</b>")
        if not is_own:
            kb.append([InlineKeyboardButton(text=f"⚙️ Права и роль: {tag}", callback_data=f"adm_st_card:{s['id']}")])
    kb.append([InlineKeyboardButton(text="➕ Добавить администратора", callback_data="adm_add_staff_start")])
    kb.append([InlineKeyboardButton(text="⬅️ В панель", callback_data="adm_back_dash")])
    await callback.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_st_card:"))
async def staff_card_view(callback: CallbackQuery):
    await callback.answer()
    db_id = int(callback.data.split(":")[1])
    target = await get_staff_by_db_id(db_id)
    if not target:
        return
    tag = f"@{target['username']}" if target.get('username') else f"ID: {target.get('tg_id')}"
    await callback.message.edit_text(
        f"👤 <b>АДМИНИСТРАТОР: {tag}</b>\n🎭 Роль: <b>{html.escape(target.get('role_title') or 'Менеджер')}</b>\n\nНастройте роль или разрешения:",
        reply_markup=build_staff_permissions_kb(target),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_preset:"))
async def apply_preset_handler(callback: CallbackQuery):
    _, db_id_str, preset_key = callback.data.split(":")
    db_id = int(db_id_str)
    await apply_staff_role_preset(db_id, preset_key)
    await callback.answer("Роль применена!")
    target = await get_staff_by_db_id(db_id)
    if target:
        tag = f"@{target['username']}" if target.get('username') else f"ID: {target.get('tg_id')}"
        await callback.message.edit_text(
            f"👤 <b>АДМИНИСТРАТОР: {tag}</b>\n🎭 Роль: <b>{html.escape(target.get('role_title') or 'Менеджер')}</b>\n\nНастройте роль или разрешения:",
            reply_markup=build_staff_permissions_kb(target),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("adm_tperm:"))
async def toggle_perm_action(callback: CallbackQuery):
    _, db_id_str, perm_key = callback.data.split(":")
    db_id = int(db_id_str)
    await toggle_staff_permission(db_id, perm_key)
    await callback.answer("Обновлено!")
    target = await get_staff_by_db_id(db_id)
    if target:
        await callback.message.edit_reply_markup(reply_markup=build_staff_permissions_kb(target))

@router.callback_query(F.data.startswith("adm_rev_st_id:"))
async def revoke_staff_by_id(callback: CallbackQuery):
    db_id = int(callback.data.split(":")[1])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET role = 'client' WHERE id = ?", (db_id,))
        await db.commit()
    await callback.answer("Права сняты!", show_alert=True)
    await staff_menu_handler(callback)

@router.callback_query(F.data == "adm_add_staff_start")
async def add_staff_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminCMSFSM.waiting_for_staff_user)
    await callback.message.edit_text("Отправьте <b>@username</b> или цифровой ID:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_staff_menu")]]), parse_mode="HTML")

@router.message(AdminCMSFSM.waiting_for_staff_user)
async def process_grant_staff(message: Message, state: FSMContext):
    username_or_id = message.text.strip()
    db_id = await set_user_role_by_username(username_or_id, role='staff', role_title='Менеджер продаж')
    await state.clear()
    target = await get_staff_by_db_id(db_id)
    await message.answer(f"✅ Администратор <b>{html.escape(username_or_id)}</b> добавлен!", parse_mode="HTML", reply_markup=build_staff_permissions_kb(target))

CALC_CATEGORIES = {
    "cat_shop": ("🛒 Магазин: 1С, Оплата, Доставка", ["goods_payment", "goods_delivery", "goods_stock", "goods_crm", "services_payment", "goods_count"]),
    "cat_features": ("⚙️ Функционал (ЛК, Квизы, Поиск)", ["goods_features", "services_popup"]),
    "cat_design": ("🎨 Дизайн и стилистика", ["design_style_page", "goods_variations"]),
    "cat_promo": ("🚀 Продвижение и реклама", ["promo_target", "promo_types_page", "promo_format_page", "promo_geo_page"]),
    "cat_fix": ("🔧 Доработка сайтов", ["fix_tasks_page"])
}

NODE_LABEL_MAP = {
    "goods_payment": "💳 Онлайн-оплата (Товары)",
    "goods_delivery": "🚚 Расчет доставки (СДЭК/Почта)",
    "goods_stock": "📊 Интеграция 1С / МойСклад",
    "goods_crm": "🔄 Интеграция с CRM (Товары)",
    "services_payment": "💳 Онлайн-оплата (Услуги)",
    "services_crm": "🔄 CRM для услуг",
    "services_popup": "💬 Всплывающие окна (Pop-up)"
}

@router.callback_query(F.data == "adm_calc_rates")
async def calc_categories_menu(callback: CallbackQuery):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_calc"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    kb = [[InlineKeyboardButton(text=cat_title, callback_data=f"adm_ccat:{cat_key}")] for cat_key, (cat_title, _) in CALC_CATEGORIES.items()]
    kb.append([InlineKeyboardButton(text="⬅️ В панель", callback_data="adm_back_dash")])
    await callback.message.edit_text("🧮 <b>НАСТРОЙКА СМЕТЫ И СРОКОВ</b>\nВыберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_ccat:"))
async def calc_category_items(callback: CallbackQuery):
    await callback.answer()
    cat_key = callback.data.split(":")[1]
    cat_title, node_ids = CALC_CATEGORIES[cat_key]
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        placeholders = ",".join("?" * len(node_ids))
        async with db.execute(f"SELECT * FROM buttons WHERE node_id IN ({placeholders}) AND (budget_weight > 0 OR timeline_days > 0 OR action_type = 'navigate') ORDER BY budget_weight DESC, id ASC", node_ids) as cursor:
            buttons = [dict(r) for r in await cursor.fetchall()]
    kb = []
    for b in buttons:
        if b["text"].strip().lower() in ("нет", "⬅️ назад"):
            continue
        display_title = NODE_LABEL_MAP.get(b["node_id"], f"Опция: {b['node_id']}") if b["text"].strip().lower() == "да" else b["text"][:26]
        p_txt = f"+{int(b['budget_weight']):,} ₽".replace(",", " ") if b['budget_weight'] > 0 else "0 ₽"
        d_txt = f"+{b['timeline_days']} дн." if b['timeline_days'] > 0 else "0 дн."
        kb.append([InlineKeyboardButton(text=f"{display_title} ({p_txt}, {d_txt})", callback_data=f"adm_ecalc:{b['id']}:{cat_key}")])
    kb.append([InlineKeyboardButton(text="⬅️ К категориям", callback_data="adm_calc_rates")])
    await callback.message.edit_text(f"⚙️ <b>{cat_title}</b>:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_ecalc:"))
async def edit_calc_item_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    btn_id, cat_key = int(parts[1]), parts[2] if len(parts) > 2 else "cat_shop"
    btn = await get_button_by_id(btn_id)
    await state.update_data(editing_btn_id=btn_id, return_cat_key=cat_key)
    await state.set_state(AdminCMSFSM.waiting_for_btn_calc)
    title = NODE_LABEL_MAP.get(btn["node_id"], btn["node_id"]) if btn["text"].strip().lower() == "да" else btn["text"]
    await callback.message.edit_text(f"⚙️ <b>{html.escape(title)}</b>\nОтправьте стоимость (₽) и дни:\n<code>20000 4</code>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"adm_ccat:{cat_key}")]]), parse_mode="HTML")

@router.message(AdminCMSFSM.waiting_for_btn_calc)
async def process_calc_weights_save(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    data = await state.get_data()
    try:
        new_budget, new_days = float(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        await update_button_weights(data.get("editing_btn_id"), new_budget, new_days)
        await state.clear()
        await message.answer(f"✅ Обновлено: +{int(new_budget):,} ₽, +{new_days} дн.".replace(",", " "), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data=f"adm_ccat:{data.get('return_cat_key', 'cat_shop')}")]]))
    except Exception:
        await message.answer("❌ Формат: <code>25000 5</code>", parse_mode="HTML")

@router.callback_query(F.data == "adm_reset_confirm")
async def reset_scenario_prompt(callback: CallbackQuery):
    await callback.answer()
    if not is_owner_filter(callback.from_user.id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ ДА, ВОССТАНОВИТЬ ЭКРАНЫ", callback_data="adm_reset_execute")],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="adm_back_dash")]
    ])
    await callback.message.edit_text("🛡 Восстановить стандартные 56 экранов? (Заявки и клиенты не пострадают)", reply_markup=kb)

@router.callback_query(F.data == "adm_reset_execute")
async def reset_scenario_exec(callback: CallbackQuery):
    await callback.answer()
    if not is_owner_filter(callback.from_user.id):
        return
    await seed_scenario_to_db(force=True)
    await callback.message.edit_text("🎉 Сценарий восстановлен!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 В панель", callback_data="adm_back_dash")]]))

@router.callback_query(F.data == "adm_export_excel")
async def export_excel_handler(callback: CallbackQuery):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_export"):
        return
    excel_stream = await generate_leads_excel()
    doc_file = BufferedInputFile(excel_stream.read(), filename="leads_agency_export.xlsx")
    await callback.message.answer_document(document=doc_file, caption="📊 <b>Выгрузка заявок агентства</b>", parse_mode="HTML")

@router.callback_query(F.data == "adm_leads_stats")
async def leads_stats_handler(callback: CallbackQuery):
    await callback.answer()
    leads = await get_all_leads(limit=1000)
    st_counts = {"new": 0, "in_progress": 0, "meeting_scheduled": 0, "deal_closed": 0, "rejected": 0}
    for l in leads:
        st = l.get("status", "new")
        st_counts[st] = st_counts.get(st, 0) + 1
    text = f"📊 <b>АНАЛИТИКА ЛИДОВ:</b>\n\n• Всего: <b>{len(leads)}</b>\n• 🆕 Новые: <b>{st_counts['new']}</b>\n• 🟡 В работе: <b>{st_counts['in_progress']}</b>\n• 📞 Созвон: <b>{st_counts['meeting_scheduled']}</b>\n• 🟢 Договор: <b>{st_counts['deal_closed']}</b>\n• 🔴 Отказ: <b>{st_counts['rejected']}</b>"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📥 Скачать Excel", callback_data="adm_export_excel")], [InlineKeyboardButton(text="⬅️ В панель", callback_data="adm_back_dash")]]) , parse_mode="HTML")

@router.callback_query(F.data == "adm_agency_settings")
async def agency_settings_menu(callback: CallbackQuery):
    await callback.answer()
    if not is_owner_filter(callback.from_user.id):
        return
    tg = await get_setting("agency_telegram", "@site_it")
    phone = await get_setting("agency_phone", "+7 999 155-10-43")
    email = await get_setting("agency_email", "site-it@mail.ru")
    routing_mode = await get_setting("leads_routing_mode", "both")
    mode_labels = {"both": "🏢 В группу + 👑 Владельцу", "group_only": "🏢 Только в группу", "owner_only": "👑 Только Владельцу", "all_staff": "📢 Всем менеджерам и в группу"}
    text = f"⚙️ <b>НАСТРОЙКИ:</b>\n\n• Маршрут: <b>{mode_labels.get(routing_mode, 'В группу + Владельцу')}</b>\n• Telegram: <b>{html.escape(tg)}</b>\n• Телефон: <code>{html.escape(phone)}</code>\n• Email: <code>{html.escape(email)}</code>"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Изменить маршрут заявок", callback_data="adm_leads_route_menu")],
        [InlineKeyboardButton(text="📱 Изменить Telegram", callback_data="adm_set_opt:agency_telegram")],
        [InlineKeyboardButton(text="📞 Изменить телефон", callback_data="adm_set_opt:agency_phone")],
        [InlineKeyboardButton(text="✉️ Изменить Email", callback_data="adm_set_opt:agency_email")],
        [InlineKeyboardButton(text="⬅️ В панель", callback_data="adm_back_dash")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "adm_leads_route_menu")
async def leads_route_menu(callback: CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 В группу + 👑 Владельцу в ЛС", callback_data="set_route:both")],
        [InlineKeyboardButton(text="🏢 Только в группу отдела продаж", callback_data="set_route:group_only")],
        [InlineKeyboardButton(text="👑 Только Владельцу в ЛС", callback_data="set_route:owner_only")],
        [InlineKeyboardButton(text="📢 Всем (группа + менеджеры в ЛС)", callback_data="set_route:all_staff")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="adm_agency_settings")]
    ])
    await callback.message.edit_text("🎯 <b>Куда отправлять новые заявки?</b>", reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("set_route:"))
async def process_route_choice(callback: CallbackQuery):
    await set_setting("leads_routing_mode", callback.data.split(":")[1])
    await callback.answer("Маршрут обновлен!", show_alert=True)
    await agency_settings_menu(callback)

@router.callback_query(F.data.startswith("adm_set_opt:"))
async def set_opt_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    opt_key = callback.data.split(":")[1]
    await state.update_data(setting_key=opt_key)
    await state.set_state(AdminCMSFSM.waiting_for_setting_value)
    await callback.message.edit_text(f"Введите значение для <code>{opt_key}</code>:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_agency_settings")]]), parse_mode="HTML")

@router.message(AdminCMSFSM.waiting_for_setting_value)
async def process_setting_value(message: Message, state: FSMContext):
    data = await state.get_data()
    await set_setting(data.get("setting_key"), message.text.strip())
    await state.clear()
    await message.answer("✅ Обновлено!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ К настройкам", callback_data="adm_agency_settings")]]))

@router.callback_query(F.data == "adm_broadcast_start")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    perms = await get_user_permissions(callback.from_user.id, callback.from_user.username or "")
    if not perms.get("can_broadcast"):
        await callback.answer("⛔ Нет прав.", show_alert=True)
        return
    await state.set_state(AdminCMSFSM.waiting_for_broadcast)
    await callback.message.edit_text("📢 Отправьте текст для рассылки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_back_dash")]]), parse_mode="HTML")

@router.message(AdminCMSFSM.waiting_for_broadcast)
async def process_broadcast_send(message: Message, state: FSMContext):
    perms = await get_user_permissions(message.from_user.id, message.from_user.username or "")
    users = await get_all_users_by_target("all")
    sent = 0
    for uid in users:
        try:
            await message.bot.send_message(uid, f"📢 <b>Новости агентства:</b>\n\n{html.escape(message.text.strip())}", parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await state.clear()
    await message.answer(f"✅ Доставлено {sent} пользователям.", reply_markup=build_dashboard_kb(perms))