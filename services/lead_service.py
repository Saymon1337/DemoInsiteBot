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
    """
    Точный расчет предварительной сметы и сроков по словарю пройденных экранов
    (_node_budgets и _node_days) без дублирования при переходах «Назад».
    """
    answers = session.get("answers", {})
    node_budgets = answers.get("_node_budgets", {})
    node_days = answers.get("_node_days", {})

    if isinstance(node_budgets, dict):
        add_budget = sum(float(v) for v in node_budgets.values())
    else:
        add_budget = float(answers.get("_calc_budget", 0.0))

    if isinstance(node_days, dict):
        add_days = sum(int(v) for v in node_days.values())
    else:
        add_days = int(answers.get("_calc_days", 0))

    branch_type = str(answers.get("new_site_type", ""))
    if "Товары и услуги" in branch_type or "combo_priority" in answers:
        base_budget = float(await get_setting("calc_base_multipage", "80000"))
        base_days = 20
    elif "Товары" in branch_type:
        base_budget = float(await get_setting("calc_base_multipage", "60000"))
        base_days = 15
    elif "Услуги" in branch_type:
        base_budget = float(await get_setting("calc_base_landing", "40000"))
        base_days = 10
    elif any(k.startswith("promo_") for k in answers.keys()):
        base_budget = float(await get_setting("calc_base_promo", "35000"))
        base_days = 7
    elif any(k.startswith("fix_") for k in answers.keys()):
        base_budget = 25000.0
        base_days = 5
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


# Полный перечень вопросов сценария в строгом порядке для карточки лида и Excel
STANDARD_QUESTIONS_ORDER = [
    ("new_site_type", "Тип сайта"),
    ("new_site_other_input", "Свой вариант типа сайта"),
    ("combo_priority", "Приоритет (Товары + Услуги)"),
    ("combo_sphere", "Сфера деятельности (Товары + Услуги)"),
    ("combo_sphere_other_input", "Своя сфера (Товары + Услуги)"),
    ("goods_payment", "Онлайн-оплата (Товары)"),
    ("goods_delivery", "Расчет доставки (СДЭК/Почта)"),
    ("goods_stock", "Учет остатков (1С/МойСклад)"),
    ("goods_crm", "Интеграция с CRM"),
    ("goods_features", "Требуемый функционал"),
    ("goods_features_other_input", "Доп. функционал (вручную)"),
    ("goods_variations", "Вариации товаров"),
    ("goods_variations_other_input", "Свои вариации товаров"),
    ("goods_count", "Количество товаров"),
    ("goods_import_format", "Передача данных товаров"),
    ("services_sphere", "Сфера услуг"),
    ("services_sphere_other_input", "Своя сфера услуг"),
    ("services_structure", "Структура сайта"),
    ("services_content", "Наполнение и тексты"),
    ("services_content_other_input", "Свое описание наполнения"),
    ("services_payment", "Оплата на сайте (Услуги)"),
    ("services_crm", "CRM и чаты (Услуги)"),
    ("services_popup", "Всплывающие окна (Pop-up)"),
    ("services_popup_count_input", "Количество и описание Pop-up окон"),
    ("sections_main_page", "Основные страницы"),
    ("sections_main_other_input", "Свой вариант (Основные страницы)"),
    ("sections_catalog_page", "Страницы услуг и товаров"),
    ("sections_catalog_other_input", "Свой вариант (Услуги и товары)"),
    ("sections_trust_page", "Доверие и отзывы"),
    ("sections_trust_other_input", "Свой вариант (Доверие и отзывы)"),
    ("sections_portfolio_page", "Портфолио и проекты"),
    ("sections_portfolio_other_input", "Свой вариант (Портфолио)"),
    ("sections_legal_page", "Правовая информация"),
    ("sections_other_input", "Дополнительные страницы (Иное)"),
    ("design_style_page", "Пожелания по дизайну"),
    ("combo_flows_page", "Разные потоки (купить / заказать услугу)"),
    ("design_examples_page", "Примеры сайтов"),
    ("input_examples_link", "Ссылка и комментарий к примеру"),
    ("input_tz_file", "Файл ТЗ"),
    ("input_examples_other", "Описание примеров в свободной форме"),
    ("promo_target", "Что продвигаем"),
    ("promo_target_other_input", "Свой объект продвижения"),
    ("promo_link_site", "Ссылка на сайт (Продвижение)"),
    ("promo_link_social", "Ссылка на соцсети"),
    ("promo_link_2gis", "Ссылка на 2ГИС"),
    ("promo_link_yabiz", "Ссылка на Яндекс Бизнес"),
    ("promo_link_yamaps", "Ссылка на Яндекс Карты"),
    ("promo_link_yaserv", "Ссылка на Яндекс Услуги"),
    ("promo_types_page", "Интересующие типы продвижения"),
    ("promo_types_other_input", "Свой тип продвижения"),
    ("promo_current_status", "Текущее продвижение"),
    ("promo_current_paid_input", "Какая платная реклама используется"),
    ("promo_current_unknown_input", "Описание текущих действий по рекламе"),
    ("promo_current_past_input", "Как продвигали раньше"),
    ("promo_helped_page", "Кто помогал с продвижением ранее"),
    ("promo_helped_other_input", "Кто помогал (свой вариант)"),
    ("promo_format_page", "Формат работы (настройка / ведение)"),
    ("promo_format_other_input", "Уточнение по формату продвижения"),
    ("promo_geo_page", "География продвижения"),
    ("promo_goals_page", "Цели рекламы"),
    ("promo_url_input", "Ссылка на сайт для анализа рекламы"),
    ("fix_platform", "Платформа/CMS сайта"),
    ("fix_platform_other_input", "Своя платформа/CMS"),
    ("fix_tasks_page", "Задачи по доработке сайта"),
    ("fix_tasks_other_input", "Свои пожелания по доработке"),
    ("fix_url_input", "Ссылка на дорабатываемый сайт"),
    ("fix_rebuild_page", "Готовность к полной пересборке"),
    ("fix_promo_status_page", "Текущее продвижение дорабатываемого сайта"),
    ("fix_promo_other_input", "Как продвигается сайт (уточнение)"),
    ("fix_access_page", "Наличие доступов от сайта"),
    ("fix_access_other_input", "Ситуация с доступами"),
    ("case_other_input", "Запрос примеров из портфолио (Иное)"),
    ("portfolio_order_choice", "Выбранная услуга из портфолио")
]


async def format_answers_summary(answers: dict) -> str:
    """
    Генератор брифа:
    1. Выводит ответы по всем стандартным вопросам сценария.
    2. Внизу отдельным блоком дописывает ответы на кастомные экраны, созданные через CMS.
    """
    ignored_keys = {
        "_calc_budget", "_calc_days", "_node_budgets", "_node_days",
        "_step_queue", "preferred_time", "tz_file_id",
        "_privacy_accepted", "final_lead_name", "final_lead_phone", "final_lead_messenger"
    }
    standard_keys_set = {k for k, _ in STANDARD_QUESTIONS_ORDER}

    lines = []

    for key, label in STANDARD_QUESTIONS_ORDER:
        if key in answers:
            val = answers[key]
            val_str = ", ".join(val) if isinstance(val, list) else str(val)
            if val_str:
                lines.append(f"• <b>{label}:</b> {html.escape(val_str)}")

    custom_lines = []
    for key, val in answers.items():
        if key in standard_keys_set or key in ignored_keys or key.startswith("_"):
            continue

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
    if any(k.startswith("promo_") for k in answers.keys()):
        branch = "Продвижение"
    elif any(k.startswith("fix_") for k in answers.keys()):
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

    # 1. Завершающее сообщение клиенту (строго по стр. 23-24 ТЗ + блок оценки проекта)
    client_text = (
        f"🎉 <b>Спасибо за заявку, {html.escape(client_name)}!</b>\n\n"
        "Мы обязательно с вами свяжемся в ближайшее время — обсудим всё подробно "
        "и предложим оптимальные варианты под ваш бюджет и цели.\n\n"
        "⚡️ <i>Вся ваша информация передана напрямую специалисту — без посредников и задержек.</i>\n\n"
        f"📊 <b>Предварительная оценка проекта:</b>\n"
        f"• Ориентировочный бюджет: <b>{budget_estimate}</b>\n"
        f"• Срок реализации: <b>{timeline_estimate}</b>\n"
        f"<i>(Точную смету с этапами оплат зафиксируем после короткого обсуждения)</i>\n\n"
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
