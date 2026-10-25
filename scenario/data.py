# Полное дерево сценария с кликабельным портфолио и умной логикой

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
            {"text": "📦 Товары", "action": "navigate", "target": "goods_payment", "budget": 60000, "days": 15, "row": 0},
            {"text": "🛠 Услуги", "action": "navigate", "target": "services_sphere", "budget": 40000, "days": 10, "row": 0},
            {"text": "📦+🛠 Товары и услуги", "action": "navigate", "target": "combo_priority", "budget": 80000, "days": 20, "row": 1},
            {"text": "✏️ Иное (ввести вручную)", "action": "navigate", "target": "new_site_other_input", "budget": 50000, "days": 12, "row": 1},
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

    # --- Подветка: ТОВАРЫ ---
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
        "text": "⚙️ <b>Какой функционал нужен?</b>\n<i>(Можно выбрать несколько вариантов)</i>",
        "type": "multiselect",
        "next_node_id": "goods_variations",
        "buttons": [
            {"text": "Подписка на рассылку", "action": "toggle", "budget": 5000, "days": 1, "row": 0},
            {"text": "Купоны/промокоды", "action": "toggle", "budget": 8000, "days": 2, "row": 0},
            {"text": "Личный кабинет", "action": "toggle", "budget": 25000, "days": 5, "row": 1},
            {"text": "Купить в 1 клик", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Поиск по сайту", "action": "toggle", "budget": 5000, "days": 1, "row": 2},
            {"text": "Квиз-опросник", "action": "toggle", "budget": 10000, "days": 2, "row": 2},
            {"text": "Онлайн-консультант", "action": "toggle", "budget": 4000, "days": 1, "row": 3},
            {"text": "Калькулятор", "action": "toggle", "budget": 15000, "days": 3, "row": 3},
            {"text": "Выбор города/языка", "action": "toggle", "budget": 12000, "days": 3, "row": 4}
        ]
    },
    {
        "id": "goods_variations",
        "text": "🎨 <b>У товаров будут вариации?</b>\n<i>(Цвета, размеры, объемы и т.п.)</i>",
        "type": "multiselect",
        "next_node_id": "goods_count",
        "buttons": [
            {"text": "Нет вариаций", "action": "toggle", "row": 0},
            {"text": "Цвет", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Размер", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Вес", "action": "toggle", "budget": 3000, "days": 1, "row": 2},
            {"text": "Объем", "action": "toggle", "budget": 3000, "days": 1, "row": 2},
            {"text": "Материал", "action": "toggle", "budget": 3000, "days": 1, "row": 3}
        ]
    },
    {
        "id": "goods_count",
        "text": "📦 <b>Сколько товаров планируется в каталоге?</b>",
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
            {"text": "Уже есть файл выгрузки", "action": "navigate", "target": "site_sections_category", "row": 0},
            {"text": "Нужно парсить с сайта", "action": "navigate", "target": "site_sections_category", "budget": 15000, "days": 3, "row": 1},
            {"text": "Пока не знаю", "action": "navigate", "target": "site_sections_category", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },

    # --- ВЫБОР РАЗДЕЛОВ И СТРАНИЦ САЙТА ---
    {
        "id": "site_sections_category",
        "text": "📑 <b>Какие разделы сайта вам понадобятся?</b>\n\nВыберите категорию для уточнения состава страниц:",
        "type": "regular",
        "buttons": [
            {"text": "Основные страницы", "action": "navigate", "target": "sections_main_page", "row": 0},
            {"text": "Услуги и товары", "action": "navigate", "target": "sections_catalog_page", "row": 0},
            {"text": "Доверие и отзывы", "action": "navigate", "target": "sections_trust_page", "row": 1},
            {"text": "Портфолио и проекты", "action": "navigate", "target": "sections_portfolio_page", "row": 1},
            {"text": "Правовая информация", "action": "navigate", "target": "sections_legal_page", "row": 2},
            {"text": "✅ Готово, перейти к дизайну ➡️", "action": "navigate", "target": "design_style_page", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "sections_main_page",
        "text": "📑 <b>Основные страницы:</b>\n<i>(Отметьте нужные пункты и нажмите Готово)</i>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "О компании / Обо мне", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Контакты", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Прайс / Цены", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Акции", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Доставка и оплата", "action": "toggle", "budget": 3000, "row": 2},
            {"text": "FAQ (Вопрос-ответ)", "action": "toggle", "budget": 3000, "row": 2}
        ]
    },
    {
        "id": "sections_catalog_page",
        "text": "📑 <b>Услуги и товары:</b>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Страницы услуг", "action": "toggle", "budget": 5000, "row": 0},
            {"text": "Каталог товаров", "action": "toggle", "budget": 8000, "row": 0},
            {"text": "Сертификаты и награды", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Бренды / Марки", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Вакансии", "action": "toggle", "budget": 3000, "row": 2}
        ]
    },
    {
        "id": "sections_trust_page",
        "text": "📑 <b>Доверие и отзывы:</b>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Блок преимуществ", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Отзывы клиентов", "action": "toggle", "budget": 3000, "row": 0},
            {"text": "Партнеры / Сотрудничество", "action": "toggle", "budget": 3000, "row": 1},
            {"text": "Новости и статьи (Блог)", "action": "toggle", "budget": 6000, "row": 1}
        ]
    },
    {
        "id": "sections_portfolio_page",
        "text": "📑 <b>Портфолио и проекты:</b>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Наши проекты", "action": "toggle", "budget": 6000, "row": 0},
            {"text": "Выполненные объекты", "action": "toggle", "budget": 6000, "row": 0},
            {"text": "Фотогалерея", "action": "toggle", "budget": 4000, "row": 1}
        ]
    },
    {
        "id": "sections_legal_page",
        "text": "📑 <b>Правовая информация:</b>",
        "type": "multiselect",
        "next_node_id": "site_sections_category",
        "buttons": [
            {"text": "Политика конфиденциальности", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Пользовательское соглашение", "action": "toggle", "budget": 2000, "row": 0},
            {"text": "Договор-оферта", "action": "toggle", "budget": 2000, "row": 1}
        ]
    },

    # --- ДИЗАЙН И ПРИМЕРЫ ---
    {
        "id": "design_style_page",
        "text": "🎨 <b>Пожелания по стилистике и дизайну:</b>",
        "type": "regular",
        "buttons": [
            {"text": "Полный индив. дизайн + логотип", "action": "navigate", "target": "design_examples_page", "budget": 45000, "days": 10, "row": 0},
            {"text": "Только логотип, дизайн предложите вы", "action": "navigate", "target": "design_examples_page", "budget": 25000, "days": 5, "row": 1},
            {"text": "Есть логотип, нужен дизайн под него", "action": "navigate", "target": "design_examples_page", "budget": 20000, "days": 4, "row": 2},
            {"text": "Главное — просто современно и красиво", "action": "navigate", "target": "design_examples_page", "budget": 15000, "days": 3, "row": 3},
            {"text": "Шаблон подойдет, бюджет ограничен", "action": "navigate", "target": "design_examples_page", "budget": 5000, "row": 4},
            {"text": "Хотелось бы проконсультироваться", "action": "navigate", "target": "design_examples_page", "row": 5},
            {"text": "⬅️ Назад", "action": "back", "row": 6}
        ]
    },
    {
        "id": "design_examples_page",
        "text": "🌟 <b>Есть ли пример сайта, который вам нравится?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, есть (отправлю ссылку)", "action": "navigate", "target": "input_examples_link", "row": 0},
            {"text": "Нет, нужна помощь с примерами", "action": "navigate", "target": "final_lead_name", "row": 1},
            {"text": "Есть подробное ТЗ (загружу файл)", "action": "navigate", "target": "input_tz_file", "row": 2},
            {"text": "Иное (опишу текстом)", "action": "navigate", "target": "input_examples_other", "row": 3},
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
        "text": "✍️ Опишите ваши пожелания и примеры в свободной форме:",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА 2: УСЛУГИ ---
    {
        "id": "services_sphere",
        "text": "🛠 <b>В какой сфере вы работаете?</b>\n\nВыберите сферу оказания услуг:",
        "type": "regular",
        "buttons": [
            {"text": "Строительство / благоустройство", "action": "navigate", "target": "services_structure", "row": 0},
            {"text": "Ремонтные работы", "action": "navigate", "target": "services_structure", "row": 0},
            {"text": "Производство / промышленность", "action": "navigate", "target": "services_structure", "row": 1},
            {"text": "Автомобили / автосервис", "action": "navigate", "target": "services_structure", "row": 1},
            {"text": "Специалисты (юристы, бьюти и др.)", "action": "navigate", "target": "services_structure", "row": 2},
            {"text": "Еда / доставка / кулинария", "action": "navigate", "target": "services_structure", "row": 2},
            {"text": "Спорт / отдых / тренеры", "action": "navigate", "target": "services_structure", "row": 3},
            {"text": "Иное (введу текстом)", "action": "navigate", "target": "services_sphere_other_input", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "services_sphere_other_input",
        "text": "✍️ Напишите, чем вы занимаетесь:",
        "type": "input_text",
        "next_node_id": "services_structure",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "services_structure",
        "text": "📐 <b>Какую структуру сайта вы рассматриваете?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Одностраничный сайт (лендинг)", "action": "navigate", "target": "services_content", "budget": 35000, "days": 7, "row": 0},
            {"text": "Многостраничный сайт", "action": "navigate", "target": "services_content", "budget": 65000, "days": 14, "row": 0},
            {"text": "Зависит от бюджета", "action": "navigate", "target": "services_content", "row": 1},
            {"text": "Затрудняюсь, нужна консультация", "action": "navigate", "target": "services_content", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "services_content",
        "text": "📝 <b>У вас есть наполнение для сайта?</b>\n<i>(Можно выбрать несколько пунктов)</i>",
        "type": "multiselect",
        "next_node_id": "services_payment",
        "buttons": [
            {"text": "Есть все тексты и материалы", "action": "toggle", "row": 0},
            {"text": "Есть частично, нужна помощь", "action": "toggle", "budget": 8000, "days": 2, "row": 0},
            {"text": "Нужны уникальные тексты под ключ", "action": "toggle", "budget": 15000, "days": 4, "row": 1},
            {"text": "Требуется подбор изображений", "action": "toggle", "budget": 5000, "days": 1, "row": 1},
            {"text": "Затрудняюсь, нужно обсудить", "action": "toggle", "row": 2}
        ]
    },
    {
        "id": "services_payment",
        "text": "💳 <b>Нужно ли подключать онлайн-оплату за услуги?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "services_crm", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "services_crm", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "services_crm",
        "text": "🔄 <b>Интеграция с CRM и онлайн-чатами?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да", "action": "navigate", "target": "services_popup", "budget": 15000, "days": 3, "row": 0},
            {"text": "Нет", "action": "navigate", "target": "services_popup", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "services_popup",
        "text": "💬 <b>Нужны ли всплывающие окна (pop-up)?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, для заявки на обратный звонок", "action": "navigate", "target": "site_sections_category", "budget": 5000, "days": 1, "row": 0},
            {"text": "Да, окна с ценами и описанием услуг", "action": "navigate", "target": "site_sections_category", "budget": 8000, "days": 2, "row": 1},
            {"text": "Нужна консультация", "action": "navigate", "target": "site_sections_category", "row": 2},
            {"text": "Не уверен(а), нужно ли мне", "action": "navigate", "target": "site_sections_category", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },

    # --- ВЕТКА: ТОВАРЫ + УСЛУГИ ---
    {
        "id": "combo_priority",
        "text": "⚖️ <b>Что будет приоритетом на сайте?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Каталог товаров", "action": "navigate", "target": "services_sphere", "row": 0},
            {"text": "Каталог услуг", "action": "navigate", "target": "services_sphere", "row": 0},
            {"text": "Примерно поровну", "action": "navigate", "target": "services_sphere", "row": 1},
            {"text": "Не знаю — нужна помощь", "action": "navigate", "target": "services_sphere", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },

    # --- ВЕТКА 3: ПРОДВИЖЕНИЕ САЙТА ---
    {
        "id": "promo_target",
        "text": (
            "🚀 <b>ПРОДВИЖЕНИЕ САЙТА И БИЗНЕСА</b>\n\n"
            "Настроим рекламу, которая окупается! Продвигаем через Яндекс.Директ, SEO и карты под ключ.\n\n"
            "<b>Что вы хотите продвигать?</b>\n<i>(Можно выбрать несколько пунктов)</i>"
        ),
        "type": "multiselect",
        "next_node_id": "promo_types_page",
        "buttons": [
            {"text": "Сайт компании", "action": "toggle", "budget": 30000, "row": 0},
            {"text": "Соцсети", "action": "toggle", "budget": 20000, "row": 0},
            {"text": "Профиль в 2ГИС", "action": "toggle", "budget": 10000, "row": 1},
            {"text": "Яндекс Бизнес / Карты", "action": "toggle", "budget": 15000, "row": 1},
            {"text": "Яндекс Услуги", "action": "toggle", "budget": 10000, "row": 2},
            {"text": "Пока нет сайта и других каналов", "action": "toggle", "row": 2}
        ]
    },
    {
        "id": "promo_types_page",
        "text": "🎯 <b>Какие типы продвижения вам интересны?</b>\n<i>(Можно выбрать несколько)</i>",
        "type": "multiselect",
        "next_node_id": "promo_current_status",
        "buttons": [
            {"text": "Контекстная реклама (Яндекс.Директ)", "action": "toggle", "budget": 35000, "row": 0},
            {"text": "SEO-оптимизация и позиции", "action": "toggle", "budget": 40000, "row": 0},
            {"text": "Карты (Яндекс Карты, 2ГИС)", "action": "toggle", "budget": 15000, "row": 1},
            {"text": "Реклама в соцсетях", "action": "toggle", "budget": 25000, "row": 1},
            {"text": "Не знаю, нужна рекомендация", "action": "toggle", "row": 2}
        ]
    },
    {
        "id": "promo_current_status",
        "text": "📊 <b>Сейчас вы уже что-то продвигаете?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, через платную рекламу", "action": "navigate", "target": "promo_format_page", "row": 0},
            {"text": "Да, через SEO-продвижение", "action": "navigate", "target": "promo_format_page", "row": 0},
            {"text": "Да, через соцсети", "action": "navigate", "target": "promo_format_page", "row": 1},
            {"text": "Продвигали раньше, сейчас нет", "action": "navigate", "target": "promo_format_page", "row": 1},
            {"text": "Никогда не продвигали", "action": "navigate", "target": "promo_geo_page", "row": 2},
            {"text": "Затрудняюсь ответить", "action": "navigate", "target": "promo_geo_page", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "promo_format_page",
        "text": "⏳ <b>Вас интересует разовая настройка или постоянное ведение?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Настройка + регулярное ведение", "action": "navigate", "target": "promo_geo_page", "budget": 35000, "row": 0},
            {"text": "Только разовая настройка", "action": "navigate", "target": "promo_geo_page", "budget": 20000, "row": 1},
            {"text": "Нужна консультация", "action": "navigate", "target": "promo_geo_page", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "promo_geo_page",
        "text": "🌍 <b>География продвижения:</b>",
        "type": "regular",
        "buttons": [
            {"text": "Один город", "action": "navigate", "target": "promo_goals_page", "row": 0},
            {"text": "Несколько регионов", "action": "navigate", "target": "promo_goals_page", "budget": 10000, "row": 0},
            {"text": "Вся Россия", "action": "navigate", "target": "promo_goals_page", "budget": 20000, "row": 1},
            {"text": "Международный рынок", "action": "navigate", "target": "promo_goals_page", "budget": 35000, "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    },
    {
        "id": "promo_goals_page",
        "text": "🎯 <b>Какие главные цели у рекламы?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Заявки с сайта", "action": "navigate", "target": "promo_url_input", "row": 0},
            {"text": "Звонки клиентов", "action": "navigate", "target": "promo_url_input", "row": 0},
            {"text": "Прямые продажи", "action": "navigate", "target": "promo_url_input", "row": 1},
            {"text": "Увеличение трафика", "action": "navigate", "target": "promo_url_input", "row": 1},
            {"text": "Всё вместе под ключ", "action": "navigate", "target": "promo_url_input", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "promo_url_input",
        "text": "🔗 Оставьте ссылку на ваш сайт или сообщество для бесплатного экспресс-аудита:",
        "type": "input_text",
        "next_node_id": "final_lead_name",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },

    # --- ВЕТКА 4: ДОРАБОТАТЬ САЙТ ---
    {
        "id": "fix_platform",
        "text": "🛠 <b>ДОРАБОТКА САЙТА</b>\n\nНа какой платформе/CMS сделан ваш сайт?",
        "type": "regular",
        "buttons": [
            {"text": "WordPress", "action": "navigate", "target": "fix_tasks_page", "row": 0},
            {"text": "Tilda", "action": "navigate", "target": "fix_tasks_page", "row": 0},
            {"text": "1С-Битрикс", "action": "navigate", "target": "fix_tasks_page", "row": 1},
            {"text": "OpenCart", "action": "navigate", "target": "fix_tasks_page", "row": 1},
            {"text": "Joomla", "action": "navigate", "target": "fix_tasks_page", "row": 2},
            {"text": "Самопис / Другая CMS", "action": "navigate", "target": "fix_tasks_page", "row": 2},
            {"text": "Не знаю, нужна помощь", "action": "navigate", "target": "fix_tasks_page", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },
    {
        "id": "fix_tasks_page",
        "text": "🔧 <b>Что именно вы хотели бы доработать?</b>\n<i>(Можно выбрать несколько)</i>",
        "type": "multiselect",
        "next_node_id": "fix_url_input",
        "buttons": [
            {"text": "Редизайн и улучшение визуала", "action": "toggle", "budget": 20000, "days": 5, "row": 0},
            {"text": "Исправить верстку и адаптив", "action": "toggle", "budget": 10000, "days": 3, "row": 0},
            {"text": "Исправить баги и ошибки", "action": "toggle", "budget": 8000, "days": 2, "row": 1},
            {"text": "Добавить страницы / блоки", "action": "toggle", "budget": 12000, "days": 3, "row": 1},
            {"text": "Подключить новый функционал", "action": "toggle", "budget": 18000, "days": 4, "row": 2},
            {"text": "Перенос на другую платформу", "action": "toggle", "budget": 35000, "days": 8, "row": 2}
        ]
    },
    {
        "id": "fix_url_input",
        "text": "🔗 Введите ссылку на ваш сайт для анализа специалистом:",
        "type": "input_text",
        "next_node_id": "fix_rebuild_page",
        "buttons": [
            {"text": "Сайт не открывается / Не помню ссылку", "action": "navigate", "target": "fix_rebuild_page", "row": 0},
            {"text": "⬅️ Назад", "action": "back", "row": 1}
        ]
    },
    {
        "id": "fix_rebuild_page",
        "text": "🏗 <b>Готовы рассмотреть полную пересборку сайта, если это выгоднее доработок?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, можно предложить и такой вариант", "action": "navigate", "target": "fix_access_page", "row": 0},
            {"text": "Нет, нужны строго доработки", "action": "navigate", "target": "fix_access_page", "row": 1},
            {"text": "Затрудняюсь, нужна консультация", "action": "navigate", "target": "fix_access_page", "row": 2},
            {"text": "⬅️ Назад", "action": "back", "row": 3}
        ]
    },
    {
        "id": "fix_access_page",
        "text": "🔑 <b>У вас есть доступы от сайта (хостинг, домен, админка)?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Да, есть все доступы", "action": "navigate", "target": "final_lead_name", "row": 0},
            {"text": "Есть только от домена / хостинга", "action": "navigate", "target": "final_lead_name", "row": 1},
            {"text": "Потерял(а) / Нужна помощь в поиске", "action": "navigate", "target": "final_lead_name", "row": 2},
            {"text": "Нет никаких доступов", "action": "navigate", "target": "final_lead_name", "row": 3},
            {"text": "⬅️ Назад", "action": "back", "row": 4}
        ]
    },

    # --- ВЕТКА 5: ПРИМЕРЫ НАШИХ РАБОТ / ПОРТФОЛИО С КНОПКАМИ ССЫЛОК (стр. 24-27) ---
    {
        "id": "portfolio_spheres",
        "text": "📂 <b>ПОРТФОЛИО НАШИХ РАБОТ</b>\n\nВ какой сфере хотите посмотреть примеры сайтов?",
        "type": "regular",
        "buttons": [
            {"text": "🏗 Строительство / благоустройство", "action": "navigate", "target": "case_construction", "row": 0},
            {"text": "🔨 Ремонтные работы", "action": "navigate", "target": "case_repair", "row": 0},
            {"text": "⚙️ Производство / промышленность", "action": "navigate", "target": "case_production", "row": 1},
            {"text": "🚗 Автомобили / автосервис", "action": "navigate", "target": "case_auto", "row": 1},
            {"text": "💼 Специалисты (юристы, бьюти)", "action": "navigate", "target": "case_specialists", "row": 2},
            {"text": "🍕 Еда / доставка / кулинария", "action": "navigate", "target": "case_food", "row": 2},
            {"text": "⚽️ Спорт / отдых / тренеры", "action": "navigate", "target": "case_sport", "row": 3},
            {"text": "⬅️ В главное меню", "action": "navigate", "target": "main_menu", "row": 4}
        ]
    },
    {
        "id": "case_construction",
        "text": "🏗 <b>Примеры сайтов по строительной тематике:</b>\n\nНажмите на кнопку любого проекта, чтобы открыть демо-сайт:",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Дома из бруса (Демо)", "action": "url", "url": "https://example.com/demo1", "row": 0},
            {"text": "🌐 Сайт №2: Укладка брусчатки (Демо)", "action": "url", "url": "https://example.com/demo2", "row": 1},
            {"text": "🌐 Сайт №3: Утепление фасадов (Демо)", "action": "url", "url": "https://example.com/demo3", "row": 2},
            {"text": "🚀 Заказать разработку сайта", "action": "navigate", "target": "new_site_type", "row": 3},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_repair",
        "text": "🔨 <b>Примеры сайтов по ремонту и отделке:</b>\n\nКликните для просмотра живого сайта:",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Капитальный ремонт квартир", "action": "url", "url": "https://example.com/repair1", "row": 0},
            {"text": "🌐 Сайт №2: Натяжные потолки с расчетом", "action": "url", "url": "https://example.com/repair2", "row": 1},
            {"text": "🌐 Сайт №3: Отделка и утепление балконов", "action": "url", "url": "https://example.com/repair3", "row": 2},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 3},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_production",
        "text": "⚙️ <b>Примеры сайтов производства:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Завод металлоконструкций", "action": "url", "url": "https://example.com/prod1", "row": 0},
            {"text": "🌐 Сайт №2: Вентиляционные системы", "action": "url", "url": "https://example.com/prod2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 2},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_auto",
        "text": "🚗 <b>Примеры сайтов по авто-тематике:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Сеть автосервисов и ТО", "action": "url", "url": "https://example.com/auto1", "row": 0},
            {"text": "🌐 Сайт №2: Шиномонтаж и хранение шин", "action": "url", "url": "https://example.com/auto2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 2},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_specialists",
        "text": "💼 <b>Примеры сайтов для специалистов:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Юридическая консультация", "action": "url", "url": "https://example.com/law1", "row": 0},
            {"text": "🌐 Сайт №2: Салон красоты и косметологии", "action": "url", "url": "https://example.com/beauty2", "row": 1},
            {"text": "🌐 Сайт №3: Сайт коуча / психолога", "action": "url", "url": "https://example.com/coach3", "row": 2},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 3},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 4}
        ]
    },
    {
        "id": "case_food",
        "text": "🍕 <b>Примеры сайтов доставки еды:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Меню ресторана с заказом", "action": "url", "url": "https://example.com/food1", "row": 0},
            {"text": "🌐 Сайт №2: Доставка правильного питания", "action": "url", "url": "https://example.com/food2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 2},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },
    {
        "id": "case_sport",
        "text": "⚽️ <b>Примеры сайтов спорта и фитнеса:</b>",
        "type": "regular",
        "buttons": [
            {"text": "🌐 Сайт №1: Персональный тренер по фитнесу", "action": "url", "url": "https://example.com/sport1", "row": 0},
            {"text": "🌐 Сайт №2: Фитнес-клуб с расписанием", "action": "url", "url": "https://example.com/sport2", "row": 1},
            {"text": "🚀 Заказать услугу", "action": "navigate", "target": "new_site_type", "row": 2},
            {"text": "⬅️ К списку сфер", "action": "navigate", "target": "portfolio_spheres", "row": 3}
        ]
    },

    # --- ВЕТКА 6: СВЯЗАТЬСЯ С НАМИ (стр. 28) ---
    {
        "id": "contacts_screen",
        "text": (
            "📞 <b>СВЯЗАТЬСЯ С НАМИ</b>\n\n"
            "Если у вас остались вопросы — напишите или позвоните нам! Мы на связи:\n\n"
            "• <b>Telegram:</b> @site_it\n"
            "• <b>Телефон:</b> +7 999 155-10-43\n"
            "• <b>Email:</b> site-it@mail.ru"
        ),
        "type": "regular",
        "buttons": [
            {"text": "🚀 Заказать новый сайт", "action": "navigate", "target": "new_site_type", "row": 0},
            {"text": "📈 Продвижение сайта", "action": "navigate", "target": "promo_target", "row": 1},
            {"text": "🔧 Доработать сайт", "action": "navigate", "target": "fix_platform", "row": 2},
            {"text": "⬅️ В главное меню", "action": "navigate", "target": "main_menu", "row": 3}
        ]
    },

    # --- ФИНАЛЬНЫЙ БЛОК: СБОР КОНТАКТОВ (стр. 23) ---
    {
        "id": "final_lead_name",
        "text": (
            "🏁 <b>Остался последний шаг!</b>\n\n"
            "Чтобы мы могли подготовить предложение и связаться с вами — "
            "пожалуйста, напишите ваше <b>Имя</b>:"
        ),
        "type": "input_text",
        "next_node_id": "final_lead_phone",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "final_lead_phone",
        "text": "📱 Укажите ваш <b>номер телефона для связи</b>:\n<i>(Мы не будем названивать — только по делу)</i>",
        "type": "input_text",
        "next_node_id": "final_lead_messenger",
        "buttons": [{"text": "⬅️ Назад", "action": "back", "row": 0}]
    },
    {
        "id": "final_lead_messenger",
        "text": "💬 <b>Какой мессенджер удобнее для связи?</b>\n<i>(Можно выбрать несколько)</i>",
        "type": "multiselect",
        "next_node_id": "final_lead_time",
        "buttons": [
            {"text": "Telegram", "action": "toggle", "row": 0},
            {"text": "WhatsApp", "action": "toggle", "row": 0},
            {"text": "Звонок по телефону", "action": "toggle", "row": 1}
        ]
    },
    {
        "id": "final_lead_time",
        "text": "⏰ <b>Когда вам удобно принять звонок или сообщение?</b>",
        "type": "regular",
        "buttons": [
            {"text": "Утро (09:00–12:00)", "action": "action", "target": "submit_lead:Утро", "row": 0},
            {"text": "День (12:00–17:00)", "action": "action", "target": "submit_lead:День", "row": 0},
            {"text": "Вечер (после 17:00)", "action": "action", "target": "submit_lead:Вечер", "row": 1},
            {"text": "Без разницы — в любое время", "action": "action", "target": "submit_lead:Любое", "row": 1},
            {"text": "⬅️ Назад", "action": "back", "row": 2}
        ]
    }
]