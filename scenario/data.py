# Полное дерево сценария в строгом соответствии со всеми 28 страницами ТЗ

SCENARIO_NODES = [
    # --- СТАРТ И ГЛАВНОЕ МЕНЮ (стр. 3) ---
    {
        "id": "privacy_block",
        "text": (
            "⚠️ <b>Перед началом:</b>\n\n"
            "Мы не передаём ваши данные третьим лицам. Вся информация используется только "
            "для подготовки предложения по вашему запросу.\n"
            "Подробнее — <a href='https://telegra.ph'>Политика конфиденциальности</a>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "⚠️ Начать", "action": "navigate", "target": "main_menu", "row": 0}
        ]
    },
    {
        "id": "main_menu",
        "text": "👋 <b>Здравствуйте! Чем можем помочь?</b>\n\nВыберите интересующее направление:",
        "type": "regular",
        "buttons": [
            {"text": "🆕 Заказать новый сайт", "action": "navigate", "target": "new_site_type", "row": 0},
            {"text": "🆕 Доработать текущий сайт", "action": "navigate", "target": "fix_platform", "row": 1},
            {"text": "🆕 Продвижение сайта", "action": "navigate", "target": "promo_target", "row": 2},
            {"text": "🆕 Примеры наших работ", "action": "navigate", "target": "portfolio_spheres", "row": 3},
            {"text": "🆕 Связаться с нами", "action": "navigate", "target": "contacts_screen", "row": 4}
        ]
    },

    # --- ВЕТКА 1: ЗАКАЗАТЬ НОВЫЙ САЙТ (стр. 3-8) ---
    {
        "id": "new_site_type",
        "text": "🌐 <b>ЗАКАЗАТЬ НОВЫЙ САЙТ</b>\n\nЧто вы хотите разместить на сайте?",
        "type": "regular",
        "buttons": [
            {"text": "📦 Товары", "action": "navigate", "target": "goods_payment", "row": 0},
            {"text": "🛠 Услуги", "action": "navigate", "target": "services_sphere", "row": 0},
            {"text": "📦+🛠 Товары и услуги", "action": "navigate", "target": "combo_priority", "row": 1},
            {"text": "✏️ Иное (ввести вручную)", "action": "navigate", "target": "new_site_other_input", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "new_site_other_input",
        "text": "✍️ Напишите, что именно вы хотите разместить на сайте:",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- Подветка: ТОВАРЫ (стр. 4-6) ---
    {
        "id": "goods_payment",
        "text": "💳 <b>Нужно ли подключать оплату на сайте?</b>\n<i>(Только для ИП и юрлиц)</i>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "goods_delivery", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "goods_delivery", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "goods_delivery",
        "text": "🚚 <b>Нужен ли расчёт стоимости доставки?</b>\n<i>(СДЭК, ПЭК, BoxBerry, Почта РФ и др.)</i>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "goods_stock", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "goods_stock", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "goods_stock",
        "text": "📊 <b>Интеграция с учётом остатков (1С, МойСклад и др.)?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "goods_crm", "budget": 30000, "days": 7, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "goods_crm", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "goods_crm",
        "text": "🔄 <b>Интеграция с другими сервисами (CRM, онлайн-чаты и пр.)?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "goods_features", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "goods_features", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "goods_features",
        "text": "⚙️ <b>Какой функционал нужен?</b>\n<i>(Можно выбрать несколько)</i>",
        "type": "multiselect",
        "next_node_id": "goods_variations",
        "buttons": [
            {"text": "Подписка на рассылку", "action": "toggle", "budget": 5000, "days": 1, "row": 0},
            {"text": "Купоны/промокоды", "action": "toggle", "budget": 8000, "days": 2, "row": 0},
            {"text": "Личный кабинет", "action": "toggle", "budget": 25000, "days": 5, "row": 1},
            {"text": "Купить в 1 клик", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Поиск", "action": "toggle", "budget": 5000, "days": 1, "row": 2},
            {"text": "Квиз", "action": "toggle", "budget": 10000, "days": 2, "row": 2},
            {"text": "Онлайн-консультант", "action": "toggle", "budget": 4000, "days": 1, "row": 3},
            {"text": "Калькулятор", "action": "toggle", "budget": 15000, "days": 3, "row": 3},
            {"text": "Выбор города/языка", "action": "toggle", "budget": 12000, "days": 3, "row": 4},
            {"text": "✏️ Другое (ввести вручную)", "action": "navigate", "target": "goods_features_other_input", "row": 5}
        ]
    },
    {
        "id": "goods_features_other_input",
        "text": "✍️ <b>Напишите, какой функционал нужен:</b>",
        "type": "input_text",
        "next_node_id": "goods_variations",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "goods_variations",
        "text": "🎨 <b>У товаров будут вариации?</b>\n<i>(Мультивыбор)</i>",
        "type": "multiselect",
        "next_node_id": "goods_count",
        "buttons": [
            {"text": "Нет", "action": "toggle", "row": 0},
            {"text": "Цвет", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Размер", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Вес", "action": "toggle", "budget": 3000, "days": 1, "row": 2},
            {"text": "Объем", "action": "toggle", "budget": 3000, "days": 1, "row": 2},
            {"text": "Материал", "action": "toggle", "budget": 3000, "days": 1, "row": 3},
            {"text": "✏️ Иное (введу)", "action": "navigate", "target": "goods_variations_other_input", "row": 4}
        ]
    },
    {
        "id": "goods_variations_other_input",
        "text": "✍️ <b>Напишите, какие вариации:</b>",
        "type": "input_text",
        "next_node_id": "goods_count",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "goods_count",
        "text": "📦 <b>Сколько товаров планируется?</b>",
        "type": "regular",
        "buttons": [
            {"text": "< 100", "action": "navigate", "target": "goods_import_format", "row": 0},
            {"text": "100–1 000", "action": "navigate", "target": "goods_import_format", "budget": 10000, "days": 2, "row": 0},
            {"text": "1 000–10 000", "action": "navigate", "target": "goods_import_format", "budget": 20000, "days": 4, "row": 1},
            {"text": "> 10 000", "action": "navigate", "target": "goods_import_format", "budget": 35000, "days": 7, "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "goods_import_format",
        "text": "📁 <b>Как передадите информацию о товарах?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Заполню Excel", "action": "navigate", "target": "site_sections_category", "row": 0},
            {"text": "Уже есть файл", "action": "navigate", "target": "site_sections_category", "row": 0},
            {"text": "Нужно парсить", "action": "navigate", "target": "site_sections_category", "budget": 15000, "days": 3, "row": 1},
            {"text": "❓ Пока не знаю", "action": "navigate", "target": "site_sections_category", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },

    # --- ВЫБОР РАЗДЕЛОВ И СТРАНИЦ САЙТА (стр. 6-7, 10-12, 15-17) ---
    {
        "id": "site_sections_category",
        "text": "📑 <b>Какие разделы сайта вам понадобятся?</b>\n\n<i>Выберите категории. Затем уточним внутри каждой.</i>",
        "type": "regular",
        "buttons": [
            {"text": "Основные страницы", "action": "navigate", "target": "sections_main_page", "row": 0},
            {"text": "Услуги и товары", "action": "navigate", "target": "sections_catalog_page", "row": 0},
            {"text": "Доверие и отзывы", "action": "navigate", "target": "sections_trust_page", "row": 1},
            {"text": "Портфолио и проекты", "action": "navigate", "target": "sections_portfolio_page", "row": 1},
            {"text": "Правовая информация", "action": "navigate", "target": "sections_legal_page", "row": 2},
            {"text": "➕ Иное", "action": "navigate", "target": "sections_other_input", "row": 2},
            {"text": "✅ Готово", "action": "navigate", "target": "design_style_page", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "sections_main_page",
        "text": "📑 <b>Основные страницы:</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "О компании / Обо мне", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Контакты", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Прайс / цены", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Акции", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Доставка и оплата", "action": "toggle", "budget": 3000, "row": 2},
            {"text": "FAQ — Часто задаваемые вопросы", "action": "toggle", "budget": 3000, "row": 2},
            {"text": "➕ Добавить свой вариант", "action": "navigate", "target": "sections_main_other_input", "row": 3}
        ]
    },
    {
        "id": "sections_main_other_input",
        "text": "✍️ <b>Напишите свой вариант для основных страниц:</b>",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "sections_catalog_page",
        "text": "📑 <b>Услуги и товары:</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Услуги", "action": "toggle", "budget": 5000, "row": 0},
            {"text": "Товары (если есть каталог)", "action": "toggle", "budget": 8000, "row": 0},
            {"text": "Сертификаты", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Бренды / марки", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Вакансии", "action": "toggle", "budget": 3000, "row": 2},
            {"text": "➕ Добавить свой вариант", "action": "navigate", "target": "sections_catalog_other_input", "row": 3}
        ]
    },
    {
        "id": "sections_catalog_other_input",
        "text": "✍️ <b>Напишите свой вариант для раздела услуг и товаров:</b>",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "sections_trust_page",
        "text": "📑 <b>Доверие и отзывы:</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Преимущества", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Отзывы", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Партнеры / сотрудничество", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Новости / статьи", "action": "toggle", "budget": 6000, "row": 1},
            {"text": "➕ Добавить свой вариант", "action": "navigate", "target": "sections_trust_other_input", "row": 2}
        ]
    },
    {
        "id": "sections_trust_other_input",
        "text": "✍️ <b>Напишите свой вариант для раздела доверия и отзывов:</b>",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "sections_portfolio_page",
        "text": "📑 <b>Портфолио и проекты:</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Наши проекты", "action": "toggle", "budget": 6000, "row": 0},
            {"text": "Работы / объекты", "action": "toggle", "budget": 6000, "row": 0},
            {"text": "Фотогалерея", "action": "toggle", "budget": 4000, "row": 1},
            {"text": "➕ Добавить свой вариант", "action": "navigate", "target": "sections_portfolio_other_input", "row": 2}
        ]
    },
    {
        "id": "sections_portfolio_other_input",
        "text": "✍️ <b>Напишите свой вариант для раздела портфолио:</b>",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "sections_legal_page",
        "text": "📑 <b>Правовая информация:</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Политика конфиденциальности", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Пользовательское соглашение", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Договор-оферта", "action": "toggle", "budget": 2000, "row": 1}
        ]
    },
    {
        "id": "sections_other_input",
        "text": "➕ <b>Иное:</b>\n\nНапишите, какие страницы ещё нужны:",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ДИЗАЙН, ПОТОКИ И ПРИМЕРЫ (стр. 8, 12, 17-18) ---
    {
        "id": "design_style_page",
        "text": "Спасибо! Переходим к следующему вопросу.\n\n🎨 <b>Пожелания по стилистике и дизайну?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Полный индивидуальный дизайн + логотип", "action": "navigate", "target": "design_examples_page", "budget": 45000, "days": 10, "row": 0},
            {"text": "Только логотип, остальное предложите вы", "action": "navigate", "target": "design_examples_page", "budget": 25000, "days": 5, "row": 1},
            {"text": "Есть логотип, нужен дизайн под него", "action": "navigate", "target": "design_examples_page", "budget": 20000, "days": 4, "row": 2},
            {"text": "Главное — просто современно и красиво", "action": "navigate", "target": "design_examples_page", "budget": 15000, "days": 3, "row": 3},
            {"text": "Шаблон подойдет, бюджет ограничен", "action": "navigate", "target": "design_examples_page", "budget": 5000, "row": 4},
            {"text": "❓ Хотелось бы проконсультироваться", "action": "navigate", "target": "design_examples_page", "row": 5},
            {"text": "⬅️ Назад", "action": "back", "row": 6}
        ]
    },
    {
        "id": "combo_flows_page",
        "text": "🔀 <b>Нужны ли разные потоки: «купить» и «заказать услугу»?</b>",
        "type": "regular",
        "buttons": [
            {"text": "✅ Да, две разные страницы", "action": "navigate", "target": "design_examples_page", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет, всё в одной системе", "action": "navigate", "target": "design_examples_page", "row": 1},
            {"text": "❓ Не уверен(а)", "action": "navigate", "target": "design_examples_page", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "design_examples_page",
        "text": "🌟 <b>Есть ли пример сайта, который вам нравится?</b>",
        "type": "regular",
        "buttons": [
            {"text": "✅ Да, есть (ссылка + комментарий)", "action": "navigate", "target": "input_examples_link", "row": 0},
            {"text": "❌ Нет, нужна помощь с примерами", "action": "navigate", "target": "final_lead_name", "row": 1},
            {"text": "📎 Есть подробное ТЗ (загрузить файл)", "action": "navigate", "target": "input_tz_file", "row": 2},
            {"text": "➕ Иное (описать текстом)", "action": "navigate", "target": "input_examples_other", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "input_examples_link",
        "text": "🔗 Отправьте ссылку на сайт-пример и напишите комментарий, что в нем нравится:",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "input_tz_file",
        "text": "📎 Пожалуйста, отправьте документ с вашим ТЗ (PDF, Word, архив или сканы):",
        "type": "input_file",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "input_examples_other",
        "text": "✍️ <b>Напишите, какие есть примеры и в каком формате:</b>",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА 2: УСЛУГИ (стр. 8-12) ---
    {
        "id": "services_sphere",
        "text": "🛠 <b>В какой сфере вы работаете?</b>\n\n<i>Выберите сферу, в которой оказываете услуги:</i>",
        "type": "regular",
        "buttons": [
            {"text": "Строительство / благоустройство", "action": "navigate", "target": "services_structure", "row": 0},
            {"text": "Ремонтные работы", "action": "navigate", "target": "services_structure", "row": 0},
            {"text": "Производство / промышленность", "action": "navigate", "target": "services_structure", "row": 1},
            {"text": "Автомобили", "action": "navigate", "target": "services_structure", "row": 1},
            {"text": "Специалисты / услуги (бьюти, юристы и т.д.)", "action": "navigate", "target": "services_structure", "row": 2},
            {"text": "Еда / доставка / кулинария", "action": "navigate", "target": "services_structure", "row": 2},
            {"text": "Спорт / отдых / тренеры", "action": "navigate", "target": "services_structure", "row": 3},
            {"text": "✏️ Иное (описать вручную)", "action": "navigate", "target": "services_sphere_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "services_sphere_other_input",
        "text": "✍️ <b>Напишите, чем вы занимаетесь:</b>",
        "type": "input_text",
        "next_node_id": "services_structure",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "services_structure",
        "text": "📐 <b>Какую структуру сайта вы рассматриваете?</b>\n<i>Это влияет на функционал и стоимость.</i>",
        "type": "regular",
        "buttons": [
            {"text": "Одностраничный сайт (лендинг)", "action": "navigate", "target": "services_content", "row": 0},
            {"text": "Многостраничный сайт", "action": "navigate", "target": "services_content", "budget": 30000, "days": 7, "row": 0},
            {"text": "Зависит от бюджета", "action": "navigate", "target": "services_content", "row": 1},
            {"text": "❓ Затрудняюсь, нужна консультация", "action": "navigate", "target": "services_content", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "services_content",
        "text": "📝 <b>У вас есть наполнение для сайта?</b>\n<i>Выберите всё, что уже есть или требуется (множественный выбор):</i>",
        "type": "multiselect",
        "next_node_id": "services_payment",
        "buttons": [
            {"text": "Есть все тексты и материалы", "action": "toggle", "row": 0},
            {"text": "Есть частично, нужна помощь в подборе", "action": "toggle", "budget": 8000, "days": 2, "row": 0},
            {"text": "Нужны уникальные тексты", "action": "toggle", "budget": 15000, "days": 4, "row": 1},
            {"text": "Требуется подбор изображений", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "❓ Затрудняюсь, нужно обсуждение", "action": "toggle", "row": 2},
            {"text": "➕ Иное (описать вручную)", "action": "navigate", "target": "services_content_other_input", "row": 3}
        ]
    },
    {
        "id": "services_content_other_input",
        "text": "✍️ <b>Напишите, какое наполнение и в каком формате есть:</b>",
        "type": "input_text",
        "next_node_id": "services_payment",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "services_payment",
        "text": "💳 <b>Нужно ли подключать оплату на сайте?</b>\n<i>(Только для ИП и юрлиц)</i>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "services_crm", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "services_crm", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "services_crm",
        "text": "🔄 <b>Интеграция с другими сервисами (CRM, онлайн-чаты и пр.)?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "services_popup", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "services_popup", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "services_popup",
        "text": (
            "💬 <b>Нужны ли всплывающие окна (pop-up)?</b>\n"
            "<i>Они могут облегчить восприятие длинных страниц, либо открываться при клике «Подробнее».</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "✅ Да, нужны окна для заявки на обратный звонок", "action": "navigate", "target": "site_sections_category", "budget": 5000, "days": 1, "row": 0},
            {"text": "Да, нужны окна с текстами/ценами об услугах (укажите сколько)", "action": "navigate", "target": "services_popup_count_input", "budget": 8000, "days": 2, "row": 1},
            {"text": "❓ Нужна консультация, не понимаю, что это", "action": "navigate", "target": "site_sections_category", "row": 2},
            {"text": "Знаю, что это, но не уверен(а), нужно ли мне", "action": "navigate", "target": "site_sections_category", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "services_popup_count_input",
        "text": "✍️ <b>Сколько и какие окна вы хотите разместить?</b>",
        "type": "input_text",
        "next_node_id": "site_sections_category",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА: ТОВАРЫ + УСЛУГИ (стр. 13-18) ---
    {
        "id": "combo_priority",
        "text": "⚖️ <b>Что будет приоритетом?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Каталог товаров", "action": "navigate", "target": "combo_sphere", "row": 0},
            {"text": "Каталог услуг", "action": "navigate", "target": "combo_sphere", "row": 0},
            {"text": "Примерно поровну", "action": "navigate", "target": "combo_sphere", "row": 1},
            {"text": "❓ Не знаю — нужна помощь", "action": "navigate", "target": "combo_sphere", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "combo_sphere",
        "text": "🛠 <b>В какой сфере вы работаете?</b>\n\n<i>Выберите сферу, в которой оказываете услуги:</i>",
        "type": "regular",
        "buttons": [
            {"text": "Строительство / благоустройство", "action": "navigate", "target": "goods_payment", "row": 0},
            {"text": "Ремонтные работы", "action": "navigate", "target": "goods_payment", "row": 0},
            {"text": "Производство / промышленность", "action": "navigate", "target": "goods_payment", "row": 1},
            {"text": "Автомобили", "action": "navigate", "target": "goods_payment", "row": 1},
            {"text": "Специалисты / услуги (бьюти, юристы и т.д.)", "action": "navigate", "target": "goods_payment", "row": 2},
            {"text": "Еда / доставка / кулинария", "action": "navigate", "target": "goods_payment", "row": 2},
            {"text": "Спорт / отдых / тренеры", "action": "navigate", "target": "goods_payment", "row": 3},
            {"text": "✏️ Иное (описать вручную)", "action": "navigate", "target": "combo_sphere_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "combo_sphere_other_input",
        "text": "✍️ <b>Напишите, чем вы занимаетесь:</b>",
        "type": "input_text",
        "next_node_id": "goods_payment",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА 3: ПРОДВИЖЕНИЕ САЙТА (стр. 18-21) ---
    {
        "id": "promo_target",
        "text": (
            "🚀 <b>ПРОДВИЖЕНИЕ САЙТА</b>\n\n"
            "<b>Настроим рекламу, которая работает!</b>\n"
            "Продвигаем ваш бизнес через Яндекс.Директ под ключ — от анализа до запуска и ведения кампаний.\n\n"
            "<b>Что вы хотите продвигать?</b>\n"
            "<i>(Выберите всё, что актуально — можно несколько вариантов. Для каждого откроется поле ввода ссылки.)</i>"
        ),
        "type": "multiselect",
        "next_node_id": "promo_types_page",
        "buttons": [
            {"text": "Сайт", "action": "toggle", "budget": 15000, "row": 0},
            {"text": "Соцсети", "action": "toggle", "budget": 10000, "row": 0},
            {"text": "Профиль в 2ГИС", "action": "toggle", "budget": 8000, "row": 1},
            {"text": "Яндекс Бизнес", "action": "toggle", "budget": 10000, "row": 1},
            {"text": "Яндекс Карты", "action": "toggle", "budget": 10000, "row": 2},
            {"text": "Яндекс Услуги", "action": "toggle", "budget": 8000, "row": 2},
            {"text": "❌ Пока нет сайта и других каналов", "action": "toggle", "row": 3},
            {"text": "❓ Не знаю, нужна рекомендация", "action": "toggle", "row": 3},
            {"text": "➕ Иное", "action": "navigate", "target": "promo_target_other_input", "row": 4}
        ]
    },
    {
        "id": "promo_target_other_input",
        "text": "✍️ <b>Введите, что именно хотите продвигать:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_site",
        "text": "🔗 <b>Введите ссылку на сайт:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_social",
        "text": "🔗 <b>Введите ссылки на ваши соцсети:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_2gis",
        "text": "🔗 <b>Введите ссылку на профиль в 2ГИС:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_yabiz",
        "text": "🔗 <b>Введите ссылку на Яндекс Бизнес:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_yamaps",
        "text": "🔗 <b>Введите ссылку на Яндекс Карты:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_link_yaserv",
        "text": "🔗 <b>Введите ссылку на Яндекс Услуги:</b>",
        "type": "input_text",
        "next_node_id": "promo_types_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_types_page",
        "text": "🎯 <b>Какие типы продвижения вам интересны?</b>\n<i>(Можно выбрать несколько вариантов)</i>",
        "type": "multiselect",
        "next_node_id": "promo_current_status",
        "buttons": [
            {"text": "Реклама в Яндекс Директ", "action": "toggle", "budget": 25000, "row": 0},
            {"text": "Реклама в 2ГИС", "action": "toggle", "budget": 10000, "row": 0},
            {"text": "Реклама в Яндекс Бизнес", "action": "toggle", "budget": 12000, "row": 1},
            {"text": "Реклама в Яндекс Картах", "action": "toggle", "budget": 12000, "row": 1},
            {"text": "Реклама в Яндекс Услугах", "action": "toggle", "budget": 10000, "row": 2},
            {"text": "Реклама в соцсетях", "action": "toggle", "budget": 20000, "row": 2},
            {"text": "SEO-продвижение", "action": "toggle", "budget": 30000, "row": 3},
            {"text": "❓ Не знаю, нужна рекомендация", "action": "toggle", "row": 3},
            {"text": "➕ Иное", "action": "navigate", "target": "promo_types_other_input", "row": 4}
        ]
    },
    {
        "id": "promo_types_other_input",
        "text": "✍️ <b>Уточните, какие типы продвижения вам интересны:</b>",
        "type": "input_text",
        "next_node_id": "promo_current_status",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_current_status",
        "text": "📊 <b>Сейчас вы уже что-то продвигаете?</b>\n<i>(Можно выбрать несколько вариантов)</i>",
        "type": "multiselect",
        "next_node_id": "promo_helped_page",
        "buttons": [
            {"text": "Да, через платную рекламу", "action": "toggle", "row": 0},
            {"text": "Да, через SEO-продвижение", "action": "toggle", "row": 0},
            {"text": "Да, через соцсети", "action": "toggle", "row": 1},
            {"text": "Да, но не знаю точно, что это", "action": "toggle", "row": 1},
            {"text": "Продвигали раньше, но сейчас нет", "action": "toggle", "row": 2},
            {"text": "Никогда не продвигали, нужна помощь", "action": "toggle", "row": 3},
            {"text": "❓ Затрудняюсь ответить, нужна консультация", "action": "toggle", "row": 4}
        ]
    },
    {
        "id": "promo_current_paid_input",
        "text": "✍️ <b>Уточните, какую именно платную рекламу используете (например, Яндекс Директ, ВК, Google):</b>",
        "type": "input_text",
        "next_node_id": "promo_helped_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_current_unknown_input",
        "text": "✍️ <b>Опишите, что делаете сейчас:</b>",
        "type": "input_text",
        "next_node_id": "promo_helped_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_current_past_input",
        "text": "✍️ <b>Опишите, как продвигали раньше:</b>",
        "type": "input_text",
        "next_node_id": "promo_helped_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_helped_page",
        "text": "🤝 <b>Вам кто-то уже помогал с продвижением?</b>\n<i>(Множественный выбор)</i>",
        "type": "multiselect",
        "next_node_id": "promo_format_page",
        "buttons": [
            {"text": "Нет, никогда не обращались", "action": "toggle", "row": 0},
            {"text": "Да, помогали сотрудники Яндекс", "action": "toggle", "row": 1},
            {"text": "Да, работали с маркетологами / SEO-специалистами", "action": "toggle", "row": 2},
            {"text": "➕ Иное", "action": "navigate", "target": "promo_helped_other_input", "row": 3}
        ]
    },
    {
        "id": "promo_helped_other_input",
        "text": "✍️ <b>Опишите, кто именно помогал с продвижением:</b>",
        "type": "input_text",
        "next_node_id": "promo_format_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_format_page",
        "text": "⏳ <b>Вас интересует разовая настройка или сопровождение?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, и настройка, и регулярное продвижение", "action": "navigate", "target": "promo_geo_page", "budget": 25000, "row": 0},
            {"text": "Только разовая настройка", "action": "navigate", "target": "promo_geo_page", "budget": 15000, "row": 1},
            {"text": "❓ Нужна консультация", "action": "navigate", "target": "promo_geo_page", "row": 2},
            {"text": "➕ Иное", "action": "navigate", "target": "promo_format_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "promo_format_other_input",
        "text": "✍️ <b>Уточните ваш запрос:</b>",
        "type": "input_text",
        "next_node_id": "promo_geo_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "promo_geo_page",
        "text": "🌍 <b>География продвижения:</b>",
        "type": "regular",
        "buttons": [
            {"text": "Один город", "action": "navigate", "target": "promo_goals_page", "row": 0},
            {"text": "Несколько регионов", "action": "navigate", "target": "promo_goals_page", "budget": 10000, "row": 0},
            {"text": "Вся Россия", "action": "navigate", "target": "promo_goals_page", "budget": 20000, "row": 1},
            {"text": "Международно", "action": "navigate", "target": "promo_goals_page", "budget": 35000, "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "promo_goals_page",
        "text": "🎯 <b>Какие цели у рекламы?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Заявки", "action": "navigate", "target": "promo_url_input", "row": 0},
            {"text": "Звонки", "action": "navigate", "target": "promo_url_input", "row": 0},
            {"text": "Продажи", "action": "navigate", "target": "promo_url_input", "row": 1},
            {"text": "Увеличение трафика", "action": "navigate", "target": "promo_url_input", "row": 1},
            {"text": "Всё вместе", "action": "navigate", "target": "promo_url_input", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "promo_url_input",
        "text": "🔗 <b>Оставьте ссылку на сайт, чтобы я проанализировала:</b>\n<i>(Введите ссылку вручную)</i>",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [
            {"text": "Пока нет сайта / Пропустить", "action": "navigate", "target": "final_lead_name", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },

    # --- ВЕТКА 4: ДОРАБОТАТЬ САЙТ (стр. 21-23) ---
    {
        "id": "fix_platform",
        "text": "🛠 <b>ДОРАБОТАТЬ САЙТ</b>\n\nНа какой платформе сделан ваш сайт?",
        "type": "regular",
        "buttons": [
            {"text": "WordPress", "action": "navigate", "target": "fix_tasks_page", "row": 0},
            {"text": "Tilda", "action": "navigate", "target": "fix_tasks_page", "row": 0},
            {"text": "OpenCart", "action": "navigate", "target": "fix_tasks_page", "row": 1},
            {"text": "Joomla", "action": "navigate", "target": "fix_tasks_page", "row": 1},
            {"text": "1С-Битрикс", "action": "navigate", "target": "fix_tasks_page", "row": 2},
            {"text": "✏️ Иное (уточнить платформу)", "action": "navigate", "target": "fix_platform_other_input", "row": 2},
            {"text": "❓ Не знаю, нужна консультация", "action": "navigate", "target": "fix_tasks_page", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "fix_platform_other_input",
        "text": "✍️ <b>Уточните, на какой платформе сайт:</b>",
        "type": "input_text",
        "next_node_id": "fix_tasks_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "fix_tasks_page",
        "text": "🔧 <b>Что именно вы хотели бы доработать?</b>\n<i>(Возможность выбрать несколько вариантов)</i>",
        "type": "multiselect",
        "next_node_id": "fix_url_input",
        "buttons": [
            {"text": "Улучшить визуал или сделать редизайн", "action": "toggle", "budget": 20000, "days": 5, "row": 0},
            {"text": "Исправить верстку, структуру, логику", "action": "toggle", "budget": 10000, "days": 3, "row": 1},
            {"text": "Исправить баги, ошибки, нерабочие функции", "action": "toggle", "budget": 8000, "days": 2, "row": 2},
            {"text": "Изменить структуру: добавить/удалить страницы", "action": "toggle", "budget": 12000, "days": 3, "row": 3},
            {"text": "➕ Добавить новый функционал (калькулятор, квиз, формы, корзина и т.д.)", "action": "toggle", "budget": 18000, "days": 4, "row": 4},
            {"text": "Нужны рекомендации специалиста", "action": "toggle", "row": 5},
            {"text": "Перенос сайта на другую платформу", "action": "toggle", "budget": 35000, "days": 8, "row": 6},
            {"text": "✏️ Иное (ввести пожелания вручную)", "action": "navigate", "target": "fix_tasks_other_input", "row": 7}
        ]
    },
    {
        "id": "fix_tasks_other_input",
        "text": "✍️ <b>Опишите ваши пожелания по доработке сайта:</b>",
        "type": "input_text",
        "next_node_id": "fix_url_input",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "fix_url_input",
        "text": "🔗 <b>Введите ссылку на ваш сайт для анализа:</b>\n\n<i>Также можно выбрать:</i>",
        "type": "input_text",
        "next_node_id": "fix_rebuild_page",
        "buttons": [
            {"text": "❓ Не помню ссылку, нужна помощь", "action": "navigate", "target": "fix_rebuild_page", "row": 0},
            {"text": "❌ Сайт не открывается, нужна помощь", "action": "navigate", "target": "fix_rebuild_page", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "fix_rebuild_page",
        "text": "🏗 <b>Готовы рассмотреть полную пересборку сайта?</b>",
        "type": "regular",
        "buttons": [
            {"text": "✅ Да, можно предложить и такой вариант", "action": "navigate", "target": "fix_promo_status_page", "row": 0},
            {"text": "Нет, нужны только доработки", "action": "navigate", "target": "fix_promo_status_page", "row": 1},
            {"text": "Затрудняюсь, нужна консультация", "action": "navigate", "target": "fix_promo_status_page", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "fix_promo_status_page",
        "text": (
            "📈 <b>Сейчас сайт продвигается?</b>\n"
            "<i>(Множественный выбор)</i>\n\n"
            "💡 <i>Учитываем продвижение, чтобы сохранить позиции при доработке.</i>"
        ),
        "type": "multiselect",
        "next_node_id": "fix_access_page",
        "buttons": [
            {"text": "Да, реклама в Яндекс Директ", "action": "toggle", "row": 0},
            {"text": "Да, в Яндекс Бизнес", "action": "toggle", "row": 0},
            {"text": "Да, SEO-продвижение", "action": "toggle", "row": 1},
            {"text": "⛔ Нет, пока не продвигаем", "action": "toggle", "row": 1},
            {"text": "✏️ Иное (опишите, как продвигаете сайт)", "action": "navigate", "target": "fix_promo_other_input", "row": 2}
        ]
    },
    {
        "id": "fix_promo_other_input",
        "text": "✍️ <b>Опишите, как продвигаете сайт:</b>",
        "type": "input_text",
        "next_node_id": "fix_access_page",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "fix_access_page",
        "text": "🔑 <b>У вас есть доступы от сайта?</b>",
        "type": "regular",
        "buttons": [
            {"text": "✅ Да, у меня есть все доступы (домен и хостинг)", "action": "navigate", "target": "final_lead_name", "row": 0},
            {"text": "Есть только доступ от домена", "action": "navigate", "target": "final_lead_name", "row": 1},
            {"text": "Есть только доступ от хостинга", "action": "navigate", "target": "final_lead_name", "row": 1},
            {"text": "❓ Не помню/потерял доступы, нужна помощь", "action": "navigate", "target": "final_lead_name", "row": 2},
            {"text": "Нет никаких доступов", "action": "navigate", "target": "final_lead_name", "row": 2},
            {"text": "✏️ Иное (опишите ситуацию с доступами)", "action": "navigate", "target": "fix_access_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "fix_access_other_input",
        "text": "✍️ <b>Опишите ситуацию с доступами:</b>",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА 5: ПРИМЕРЫ НАШИХ РАБОТ / ПОРТФОЛИО (стр. 24-28) ---
    {
        "id": "portfolio_spheres",
        "text": "📂 <b>ПРИМЕРЫ НАШИХ РАБОТ</b>\n\nВ какой сфере хотите посмотреть примеры сайтов?",
        "type": "regular",
        "buttons": [
            {"text": "🏗 Строительство / благоустройство", "action": "navigate", "target": "case_construction", "row": 0},
            {"text": "🔨 Ремонтные работы", "action": "navigate", "target": "case_repair", "row": 0},
            {"text": "⚙️ Производство / промышленность", "action": "navigate", "target": "case_production", "row": 1},
            {"text": "🚗 Автомобили", "action": "navigate", "target": "case_auto", "row": 1},
            {"text": "💼 Специалисты / услуги (бьюти, юристы и т.д.)", "action": "navigate", "target": "case_specialists", "row": 2},
            {"text": "🍕 Еда / доставка / кулинария", "action": "navigate", "target": "case_food", "row": 2},
            {"text": "⚽️ Спорт / отдых / тренеры", "action": "navigate", "target": "case_sport", "row": 3},
            {"text": "✏️ Иное", "action": "navigate", "target": "case_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "navigate", "target": "main_menu", "row": 4}
        ]
    },
    {
        "id": "case_construction",
        "text": (
            "🏗 <b>Вот несколько примеров сайтов по строительной тематике:</b>\n\n"
            "• Сайт №1 – Дома под ключ\n"
            "• Сайт №2 – Укладка брусчатки\n"
            "• Сайт №3 – Утепление фасадов\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Дома под ключ", "action": "url", "url": "https://example.com/demo1", "row": 0},
            {"text": "🌐 Сайт №2 – Укладка брусчатки", "action": "url", "url": "https://example.com/demo2", "row": 1},
            {"text": "🌐 Сайт №3 – Утепление фасадов", "action": "url", "url": "https://example.com/demo3", "row": 2},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 3},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_repair",
        "text": (
            "🔨 <b>Вот несколько примеров сайтов по ремонтной тематике:</b>\n\n"
            "• Сайт №1 – Ремонт квартир\n"
            "• Сайт №2 – Натяжные потолки\n"
            "• Сайт №3 – Отделка балконов\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Ремонт квартир", "action": "url", "url": "https://example.com/repair1", "row": 0},
            {"text": "🌐 Сайт №2 – Натяжные потолки", "action": "url", "url": "https://example.com/repair2", "row": 1},
            {"text": "🌐 Сайт №3 – Отделка балконов", "action": "url", "url": "https://example.com/repair3", "row": 2},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 3},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_production",
        "text": (
            "⚙️ <b>Вот несколько примеров сайтов по тематике производства / промышленности:</b>\n\n"
            "• Сайт №1 – Производство металлоконструкций\n"
            "• Сайт №2 – Инженерные системы\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Производство металлоконструкций", "action": "url", "url": "https://example.com/prod1", "row": 0},
            {"text": "🌐 Сайт №2 – Инженерные системы", "action": "url", "url": "https://example.com/prod2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 2},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_auto",
        "text": (
            "🚗 <b>Вот несколько примеров сайтов по автомобильной тематике:</b>\n\n"
            "• Сайт №1 – Автосервис\n"
            "• Сайт №2 – Шиномонтаж и ТО\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Автосервис", "action": "url", "url": "https://example.com/auto1", "row": 0},
            {"text": "🌐 Сайт №2 – Шиномонтаж и ТО", "action": "url", "url": "https://example.com/auto2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 2},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_specialists",
        "text": (
            "💼 <b>Вот несколько примеров сайтов по тематике «специалисты»:</b>\n\n"
            "• Сайт №1 – Консультант-юрист\n"
            "• Сайт №2 – Бьюти\n"
            "• Сайт №3 – Коуч/психолог\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Консультант-юрист", "action": "url", "url": "https://example.com/law1", "row": 0},
            {"text": "🌐 Сайт №2 – Бьюти", "action": "url", "url": "https://example.com/beauty2", "row": 1},
            {"text": "🌐 Сайт №3 – Коуч/психолог", "action": "url", "url": "https://example.com/coach3", "row": 2},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 3},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_food",
        "text": (
            "🍕 <b>Вот несколько примеров сайтов по тематике еды и кулинарии:</b>\n\n"
            "• Сайт №1 – Кафе / меню\n"
            "• Сайт №2 – Доставка обедов\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Кафе / меню", "action": "url", "url": "https://example.com/food1", "row": 0},
            {"text": "🌐 Сайт №2 – Доставка обедов", "action": "url", "url": "https://example.com/food2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 2},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_sport",
        "text": (
            "⚽️ <b>Вот несколько примеров сайтов по тематике спорта и отдыха:</b>\n\n"
            "• Сайт №1 – Персональный тренер\n"
            "• Сайт №2 – Фитнес-клуб\n\n"
            "<i>Каждый сайт делался под конкретные задачи клиента. Можно адаптировать стиль под вашу нишу.</i>"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1 – Персональный тренер", "action": "url", "url": "https://example.com/sport1", "row": 0},
            {"text": "🌐 Сайт №2 – Фитнес-клуб", "action": "url", "url": "https://example.com/sport2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 2},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_other_input",
        "text": "✍️ <b>Введите, что именно вас интересует — и я пришлю примеры, если есть подходящие сайты в портфолио:</b>",
        "type": "input_text",
        "next_node_id": "portfolio_order_choice",
        "buttons": [
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "portfolio_order_choice", "row": 0},
            {"text": "⬅️ Назад к списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 1}
        ]
    },
    {
        "id": "portfolio_order_choice",
        "text": "🎯 <b>Отлично! Давайте определим, что вам нужно:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🆕 Создать новый сайт", "action": "navigate", "target": "new_site_type", "row": 0},
            {"text": "🔧 Доработать текущий сайт", "action": "navigate", "target": "fix_platform", "row": 1},
            {"text": "📈 Продвижение сайта", "action": "navigate", "target": "promo_target", "row": 2},
            {"text": "🏠 В главное меню", "action": "navigate", "target": "main_menu", "row": 3}
        ]
    },

    # --- ВЕТКА 6: СВЯЗАТЬСЯ С НАМИ (стр. 28) ---
    {
        "id": "contacts_screen",
        "text": (
            "📞 <b>Связаться с нами</b>\n\n"
            "Если у вас остались вопросы — пишите или звоните!\n"
            "Мы на связи и с радостью поможем 🤝\n\n"
            "<b>Контакты:</b>\n"
            "• <b>Telegram:</b> @site_it\n"
            "• <b>Телефон:</b> +7 999 155-10-43\n"
            "• <b>Email:</b> site-it@mail.ru"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🏠 В главное меню", "action": "navigate", "target": "main_menu", "row": 0},
            {"text": "🚀 Заказать сайт", "action": "navigate", "target": "new_site_type", "row": 1},
            {"text": "📈 Продвижение сайта", "action": "navigate", "target": "promo_target", "row": 2},
            {"text": "🔧 Доработать сайт", "action": "navigate", "target": "fix_platform", "row": 3}
        ]
    },

    # --- ФИНАЛЬНЫЙ БЛОК: СБОР КОНТАКТОВ (стр. 23) ---
    {
        "id": "final_lead_name",
        "text": (
            "🏁 <b>Остался последний шаг!</b>\n\n"
            "Чтобы мы могли с вами связаться и обсудить детали — пожалуйста, оставьте свои контактные данные.\n\n"
            "<b>Ваше имя:</b>\n<i>(введите текстом в поле ниже)</i>"
        ),
        "type": "input_text",
        "next_node_id": "final_lead_phone",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "final_lead_phone",
        "text": "📱 <b>Номер телефона для связи:</b>\n<i>Мы не будем названивать — только по делу!</i>",
        "type": "input_text",
        "next_node_id": "final_lead_messenger",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "final_lead_messenger",
        "text": "💬 <b>Удобный мессенджер для связи:</b>\n<i>(можно выбрать один или несколько)</i>",
        "type": "multiselect",
        "next_node_id": "final_lead_time",
        "buttons": [
            {"text": "WhatsApp", "action": "toggle", "row": 0},
            {"text": "Telegram", "action": "toggle", "row": 0},
            {"text": "Звонки", "action": "toggle", "row": 1}
        ]
    },
    {
        "id": "final_lead_time",
        "text": "⏰ <b>Когда вам удобно связаться?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Утро (09:00–12:00)", "action": "action", "target": "submit_lead:Утро (09:00–12:00)", "row": 0},
            {"text": "День (12:00–17:00)", "action": "action", "target": "submit_lead:День (12:00–17:00)", "row": 0},
            {"text": "Вечер (после 17:00)", "action": "action", "target": "submit_lead:Вечер (после 17:00)", "row": 1},
            {"text": "Без разницы — пишите в любое время", "action": "action", "target": "submit_lead:В любое время", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    }
]
