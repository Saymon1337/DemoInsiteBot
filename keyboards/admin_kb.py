from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_admin_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛠 Панель управления")]],
        resize_keyboard=True
    )

def get_admin_dashboard_kb(perms: dict = None) -> InlineKeyboardMarkup:
    perms = perms or {"is_owner": True, "can_leads": True, "can_calc": True, "can_content": True, "can_broadcast": True, "can_export": True}
    is_owner = perms.get("is_owner", False)

    kb = []
    
    # 1. Выгрузка в Excel (если есть право)
    if perms.get("can_export"):
        kb.append([InlineKeyboardButton(text="📥 База лидов в Excel", callback_data="adm_export_excel")])

    # 2. Настройка сметы и Персонал
    row2 = []
    if perms.get("can_calc"):
        row2.append(InlineKeyboardButton(text="🧮 Настройка сметы", callback_data="adm_calc_rates"))
    if is_owner:
        row2.append(InlineKeyboardButton(text="👥 Персонал и права", callback_data="adm_staff_menu"))
    if row2:
        kb.append(row2)

    # 3. Настройки агентства и Аналитика
    row3 = []
    if is_owner:
        row3.append(InlineKeyboardButton(text="⚙️ Настройки агентства", callback_data="adm_agency_settings"))
    if perms.get("can_leads"):
        row3.append(InlineKeyboardButton(text="📊 Аналитика лидов", callback_data="adm_leads_stats"))
    if row3:
        kb.append(row3)

    # 4. Рассылка и переход к боту
    row4 = []
    if perms.get("can_broadcast"):
        row4.append(InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast_start"))
    row4.append(InlineKeyboardButton(text="🌐 К боту", callback_data="adm_jump_bot"))
    kb.append(row4)

    # 5. Сброс к заводским — СТРОГО ТОЛЬКО ВЛАДЕЛЕЦ
    if is_owner:
        kb.append([InlineKeyboardButton(text="🔄 Сброс сценария к заводским", callback_data="adm_reset_confirm")])

    kb.append([InlineKeyboardButton(text="❌ Закрыть панель", callback_data="adm_close")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_main_kb(is_owner: bool = False) -> InlineKeyboardMarkup:
    return get_admin_dashboard_kb({"is_owner": is_owner, "can_leads": True, "can_calc": is_owner, "can_content": is_owner, "can_broadcast": is_owner, "can_export": True})

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

# Карточка управления правами конкретного сотрудника
def get_staff_perm_card_kb(staff_user: dict) -> InlineKeyboardMarkup:
    u_id = staff_user["id"]
    can_leads = "✅" if staff_user.get("can_leads", 1) else "⬜"
    can_calc = "✅" if staff_user.get("can_calc", 0) else "⬜"
    can_content = "✅" if staff_user.get("can_content", 0) else "⬜"
    can_broadcast = "✅" if staff_user.get("can_broadcast", 0) else "⬜"
    can_export = "✅" if staff_user.get("can_export", 1) else "⬜"

    kb = [
        [InlineKeyboardButton(text=f"{can_leads} Заявки и CRM", callback_data=f"adm_tperm:{u_id}:can_leads")],
        [InlineKeyboardButton(text=f"{can_export} Выгрузка в Excel", callback_data=f"adm_tperm:{u_id}:can_export")],
        [InlineKeyboardButton(text=f"{can_calc} Настройка сметы и сроков", callback_data=f"adm_tperm:{u_id}:can_calc")],
        [InlineKeyboardButton(text=f"{can_content} Редактор экранов (CMS)", callback_data=f"adm_tperm:{u_id}:can_content")],
        [InlineKeyboardButton(text=f"{can_broadcast} Массовая рассылка", callback_data=f"adm_tperm:{u_id}:can_broadcast")],
        [InlineKeyboardButton(text="❌ Снять все права сотрудника", callback_data=f"adm_rev_st_id:{u_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к списку персонала", callback_data="adm_staff_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)