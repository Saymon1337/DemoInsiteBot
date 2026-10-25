import html
import re
import logging
from aiogram import Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import OWNER_ID
from database.queries import (
    get_or_create_session, create_lead, get_setting, reset_session, 
    get_staff_and_owner_ids, get_node
)
from keyboards.engine_kb import get_lead_card_kb

logger = logging.getLogger(__name__)

async def calculate_project_estimate(session: dict) -> tuple[str, str]:
    answers = session.get("answers", {})
    add_budget = float(answers.get("_calc_budget", 0.0))
    add_days = int(answers.get("_calc_days", 0))

    branch_type = answers.get("new_site_type", "")
    if "Товары" in branch_type or "combo" in str(answers):
        base_budget = float(await get_setting("calc_base_multipage", "80000"))
        base_days = 20
    elif "Услуги" in branch_type or "Лендинг" in str(answers):
        base_budget = float(await get_setting("calc_base_landing", "40000"))
        base_days = 10
    elif "promo" in str(answers):
        base_budget = float(await get_setting("calc_base_promo", "35000"))
        base_days = 7
    else:
        base_budget = 35000.0
        base_days = 7

    total_min = int(base_budget + add_budget)
    total_max = int(total_min * 1.3)
    total_days = base_days + add_days
    weeks = max(1, round(total_days / 7))

    budget_str = f"{total_min:,} – {total_max:,} ₽".replace(",", " ")
    timeline_str = f"{weeks}–{weeks + 1} нед."
    return budget_str, timeline_str

# Базовые стандартные вопросы сценария в строгом порядке
STANDARD_QUESTIONS_ORDER = [
    ("new_site_type", "Тип сайта"),
    ("new_site_other_input", "Свой вариант типа сайта"),
    ("goods_payment", "Онлайн-оплата (Товары)"),
    ("goods_delivery", "Расчет доставки (СДЭК/Почта)"),
    ("goods_stock", "Учет остатков (1С/МойСклад)"),
    ("goods_crm", "Интеграция с CRM"),
    ("goods_features", "Требуемый функционал"),
    ("goods_variations", "Вариации товаров"),
    ("goods_count", "Количество товаров"),
    ("goods_import_format", "Передача данных товаров"),
    ("services_sphere", "Сфера услуг"),
    ("services_sphere_other_input", "Своя сфера услуг"),
    ("services_structure", "Структура сайта"),
    ("services_content", "Наполнение и тексты"),
    ("services_payment", "Оплата услуг"),
    ("services_crm", "CRM для услуг"),
    ("services_popup", "Всплывающие окна (Pop-up)"),
    ("combo_priority", "Приоритет каталога"),
    ("sections_main_page", "Основные страницы"),
    ("sections_catalog_page", "Страницы услуг/товаров"),
    ("sections_trust_page", "Блоки доверия и отзывов"),
    ("sections_portfolio_page", "Разделы портфолио"),
    ("sections_legal_page", "Правовая информация"),
    ("design_style_page", "Пожелания по дизайну"),
    ("design_examples_page", "Примеры сайтов"),
    ("input_examples_link", "Ссылка на пример сайта"),
    ("input_examples_other", "Описание примера"),
    ("promo_target", "Объекты продвижения"),
    ("promo_types_page", "Интересующие каналы рекламы"),
    ("promo_current_status", "Текущий статус рекламы"),
    ("promo_format_page", "Формат работы"),
    ("promo_geo_page", "География рекламы"),
    ("promo_goals_page", "Цели продвижения"),
    ("promo_url_input", "Ссылка на аудит рекламы"),
    ("fix_platform", "CMS текущего сайта"),
    ("fix_tasks_page", "Список задач на доработку"),
    ("fix_url_input", "Ссылка на дорабатываемый сайт"),
    ("fix_rebuild_page", "Готовность к пересборке"),
    ("fix_access_page", "Наличие доступов")
]

async def format_answers_summary(answers: dict) -> str:
    """
    Умный генератор брифа:
    1. Сначала выводит базовые стандартные вопросы из ТЗ.
    2. Затем внизу отдельным блоком дописывает ВСЕ кастомные вопросы админа (текст и чекбоксы).
    """
    ignored_keys = {
        "_calc_budget", "_calc_days", "preferred_time", "tz_file_id", 
        "_privacy_accepted", "final_lead_name", "final_lead_phone", "final_lead_messenger"
    }
    standard_keys_set = {k for k, _ in STANDARD_QUESTIONS_ORDER}

    lines = []

    # 1. СТАНДАРТНАЯ ЧАСТЬ БРИФА (СВЕРХУ)
    for key, label in STANDARD_QUESTIONS_ORDER:
        if key in answers:
            val = answers[key]
            val_str = ", ".join(val) if isinstance(val, list) else str(val)
            if val_str:
                lines.append(f"• <b>{label}:</b> {html.escape(val_str)}")

    # 2. КАСТОМНАЯ ЧАСТЬ: ВСЕ ДОБАВЛЕННЫЕ ВЛАДЕЛЬЦЕМ ЭКРАНЫ (ВНИЗУ)
    custom_lines = []
    for key, val in answers.items():
        if key in standard_keys_set or key in ignored_keys:
            continue
        
        # Получаем живой текст экрана из базы, чтобы бриф был понятным
        node = await get_node(key)
        if node and node.get("text"):
            raw_text = node["text"]
            clean_title = re.sub(r"<[^>]+>", "", raw_text).strip().replace("\n", " ")
            if len(clean_title) > 55:
                clean_title = clean_title[:52] + "..."
        else:
            clean_title = f"Доп. вопрос ({key})"

        val_str = ", ".join(val) if isinstance(val, list) else str(val)
        if val_str:
            custom_lines.append(f"• <b>{html.escape(clean_title)}:</b> {html.escape(val_str)}")

    if custom_lines:
        lines.append("\n<b>📝 Дополнительные вопросы от агентства:</b>")
        lines.extend(custom_lines)

    return "\n".join(lines) if lines else "Ответы не зафиксированы"

async def finalize_lead_submission(bot: Bot, user_id: int, callback: CallbackQuery = None, message: Message = None):
    session = await get_or_create_session(user_id)
    answers = session.get("answers", {})

    client_name = answers.get("final_lead_name", "Клиент")
    client_phone = answers.get("final_lead_phone", "Не указан")
    messenger_list = answers.get("final_lead_messenger", [])
    messenger_str = ", ".join(messenger_list) if isinstance(messenger_list, list) else str(messenger_list)
    preferred_time = answers.get("preferred_time", "В любое время")
    tz_file_id = answers.get("tz_file_id", "")

    budget_estimate, timeline_estimate = await calculate_project_estimate(session)
    answers_summary = await format_answers_summary(answers)

    branch = "Новый сайт"
    if "promo" in str(answers):
        branch = "Продвижение"
    elif "fix" in str(answers):
        branch = "Доработка сайта"

    username = callback.from_user.username if callback else (message.from_user.username if message else "")
    lead_code = await create_lead(
        user_id=user_id,
        username=username or "",
        client_name=client_name,
        client_phone=client_phone,
        messenger=messenger_str or "Не выбран",
        preferred_time=preferred_time,
        branch=branch,
        tz_file_id=tz_file_id,
        answers_summary=answers_summary,
        budget_estimate=f"{budget_estimate} ({timeline_estimate})"
    )

    # 1. Ответ клиенту
    client_text = (
        f"🎉 <b>Спасибо за заявку, {html.escape(client_name)}!</b>\n\n"
        "Мы обязательно с вами свяжемся в ближайшее время — обсудим всё подробно "
        "и предложим оптимальные варианты под ваш бюджет и цели.\n\n"
        "⚡️ <i>Вся ваша информация передана напрямую специалисту — без посредников и задержек.</i>\n\n"
        f"📊 <b>Предварительная оценка проекта:</b>\n"
        f"• Ориентировочный бюджет: <b>{budget_estimate}</b>\n"
        f"• Срок реализации: <b>{timeline_estimate}</b>\n"
        f"<i>(Точную смету с этапами оплат зафиксируем на коротком звонке)</i>\n\n"
        "💬 Если появятся дополнительные вопросы — смело пишите сюда, бот всегда на связи."
    )

    client_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="btn_nav_main")],
        [InlineKeyboardButton(text="📂 Примеры наших работ", callback_data="btn_nav_portfolio")],
        [InlineKeyboardButton(text="📞 Связаться напрямую", callback_data="btn_nav_contacts")]
    ])

    if callback and callback.message:
        try:
            await callback.message.edit_text(client_text, reply_markup=client_kb, parse_mode="HTML")
        except Exception:
            await bot.send_message(user_id, client_text, reply_markup=client_kb, parse_mode="HTML")
    else:
        await bot.send_message(user_id, client_text, reply_markup=client_kb, parse_mode="HTML")

    # 2. Формируем список получателей заявки
    routing_mode = await get_setting("leads_routing_mode", "both")
    leads_target = await get_setting("leads_channel_id", "")
    group_id = int(leads_target) if leads_target and (leads_target.lstrip("-").isdigit()) else None

    target_chat_ids = set()
    if routing_mode == "owner_only":
        target_chat_ids.add(OWNER_ID)
    elif routing_mode == "group_only":
        target_chat_ids.add(group_id or OWNER_ID)
    elif routing_mode == "all_staff":
        target_chat_ids.add(OWNER_ID)
        if group_id:
            target_chat_ids.add(group_id)
        target_chat_ids.update(await get_staff_and_owner_ids())
    else:  # "both"
        target_chat_ids.add(OWNER_ID)
        if group_id:
            target_chat_ids.add(group_id)

    # 3. Карточка менеджера (с защитой от превышения лимита 4096 символов)
    user_link = f"@{username}" if username else f"<a href='tg://user?id={user_id}'>Ссылка на профиль</a>"
    base_info = (
        f"🔥 <b>НОВАЯ ЗАЯВКА {lead_code}</b>\n\n"
        f"👤 <b>Клиент:</b> {html.escape(client_name)} ({user_link})\n"
        f"📞 <b>Телефон:</b> <code>{html.escape(client_phone)}</code>\n"
        f"💬 <b>Связь через:</b> {html.escape(messenger_str or 'Не указан')}\n"
        f"⏰ <b>Удобное время:</b> {html.escape(preferred_time)}\n"
        f"📁 <b>Направление:</b> {branch}\n\n"
        f"💰 <b>Смета:</b> {budget_estimate} ({timeline_estimate})\n\n"
        f"📋 <b>БРИФ:</b>\n"
    )

    # Защита от лимита Telegram: обрезаем бриф, если текст слишком длинный
    max_summary_len = 4000 - len(base_info)
    if len(answers_summary) > max_summary_len:
        answers_summary = answers_summary[:max_summary_len - 50] + "\n... <i>(полный бриф сохранен в Excel-выгрузке)</i>"

    manager_card = base_info + answers_summary

    for dest_id in target_chat_ids:
        try:
            await bot.send_message(
                chat_id=dest_id,
                text=manager_card,
                reply_markup=get_lead_card_kb(lead_code),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            if tz_file_id:
                await bot.send_document(
                    chat_id=dest_id,
                    document=tz_file_id,
                    caption=f"📎 Техническое задание от клиента к заявке {lead_code}"
                )
        except Exception as e:
            logger.error(f"Не удалось доставить заявку {lead_code} адресату {dest_id}: {e}")

    await reset_session(user_id, keep_privacy=True)