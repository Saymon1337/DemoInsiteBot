import re
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def is_valid_telegram_button_url(url: str) -> bool:
    """Проверяет валидность URL-ссылки для инлайн-кнопки Telegram."""
    if not url:
        return False
    u = url.strip()
    if u.startswith("tg://"):
        return True
    pattern = re.compile(
        r"^https?://[a-zA-Z0-9\-_]+(\.[a-zA-Z0-9\-_]+)+([/?].*)?$",
        re.IGNORECASE
    )
    return bool(pattern.match(u))

def build_node_keyboard(node: dict, buttons: list[dict], selected_items: list[str] = None, is_admin: bool = False, is_client_preview: bool = False) -> InlineKeyboardMarkup:
    if not node:
        node = {}
        
    selected_items = selected_items or []
    node_type = node.get("node_type", "regular")
    node_id = node.get("id", "main_menu")

    rows_dict = {}
    has_back_button = False

    for btn in buttons:
        r_idx = btn.get("row_idx", 0)
        if r_idx not in rows_dict:
            rows_dict[r_idx] = []

        btn_id = btn["id"]
        btn_text = btn["text"]
        action = btn.get("action_type", "navigate")
        url_link = btn.get("url", "")

        if action == "back":
            has_back_button = True

        if node_type == "multiselect" and action == "toggle":
            is_checked = (btn_text in selected_items)
            icon = "✅ " if is_checked else "⬜ "
            rows_dict[r_idx].append(InlineKeyboardButton(text=f"{icon}{btn_text}", callback_data=f"tog:{btn_id}"))
        elif action == "url":
            safe_url = url_link if is_valid_telegram_button_url(url_link) else "https://t.me"
            rows_dict[r_idx].append(InlineKeyboardButton(text=btn_text, url=safe_url))
        else:
            rows_dict[r_idx].append(InlineKeyboardButton(text=btn_text, callback_data=f"btn:{btn_id}"))

    keyboard_grid = [rows_dict[r] for r in sorted(rows_dict.keys())]

    # Для мультивыбора всегда добавляем кнопку Готово
    if node_type == "multiselect":
        keyboard_grid.append([InlineKeyboardButton(text="✅ Готово, продолжить ➡️", callback_data="multi_done")])

    # Если это не главное меню и нет кнопки Назад — автоматически добавляем ее для клиента
    if node_id not in ("main_menu", "privacy_block") and not has_back_button:
        keyboard_grid.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="btn_back")])

    # 1. Если это режим просмотра глазами клиента — показываем кнопки возврата в админку!
    if is_client_preview:
        keyboard_grid.append([
            InlineKeyboardButton(text="🛠 Вернуться в редактор", callback_data=f"adm_preview_node:{node_id}")
        ])
        keyboard_grid.append([
            InlineKeyboardButton(text="🚪 В главное меню админки", callback_data="adm_back_dash")
        ])

    # 2. Если это полноценный режим редактора администратора
    elif is_admin:
        keyboard_grid.append([
            InlineKeyboardButton(text="✏️ Текст", callback_data=f"adm_edit_txt:{node_id}"),
            InlineKeyboardButton(text="➕ Кнопка", callback_data=f"adm_add_btn:{node_id}"),
            InlineKeyboardButton(text="⚙️ Кнопки", callback_data=f"adm_list_btns:{node_id}")
        ])
        keyboard_grid.append([
            InlineKeyboardButton(text="👁 Вид клиента", callback_data=f"adm_client_view:{node_id}"),
            InlineKeyboardButton(text="🗑 Удалить экран", callback_data=f"adm_del_node:{node_id}")
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_grid)

def get_lead_card_kb(lead_code: str) -> InlineKeyboardMarkup:
    clean_code = lead_code.lstrip("#")
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🙋‍♂️ Взять в работу", callback_data=f"crm_take:{clean_code}"),
            InlineKeyboardButton(text="📞 Созвон назначен", callback_data=f"crm_call:{clean_code}")
        ],
        [
            InlineKeyboardButton(text="🟢 Договор подписан", callback_data=f"crm_deal:{clean_code}"),
            InlineKeyboardButton(text="🔴 Отказ / Нецелевой", callback_data=f"crm_reject:{clean_code}")
        ]
    ])