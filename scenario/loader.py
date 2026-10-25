import logging
from database.db import get_db
from scenario.data import SCENARIO_NODES

logger = logging.getLogger(__name__)

CURRENT_SCENARIO_VERSION = "v2_full_tz"


def validate_scenario_graph():
    """Автоматическая валидация графа сценария до старта бота."""
    node_ids = {n["id"] for n in SCENARIO_NODES}
    errors = []

    for node in SCENARIO_NODES:
        n_id = node["id"]
        auto_next = node.get("next_node_id")
        if auto_next and auto_next not in node_ids:
            errors.append(f"Экран '{n_id}' ссылается на несуществующий next_node_id: '{auto_next}'")

        for btn in node.get("buttons", []):
            action = btn.get("action")
            target = btn.get("target")
            if action == "navigate" and target not in node_ids:
                errors.append(f"Кнопка '{btn.get('text')}' на экране '{n_id}' ведет в никуда: '{target}'")

    if errors:
        for err in errors:
            logger.error(f"❌ ОШИБКА ГРАФА: {err}")
        raise ValueError(f"Сценарий содержит {len(errors)} ошибок целостности графа!")

    print(f"✅ Граф сценария ({len(SCENARIO_NODES)} экранов) полностью валиден! Ошибок нет.")


async def seed_scenario_to_db(force: bool = False):
    """
    Умная синхронизация базы через единое соединение get_db():
    - Если force=True (кнопка сброса к заводским) или версия сценария устарела — обновляет базовые экраны и кнопки.
    - Если force=False (обычный перезапуск) — вставляет кнопки ТОЛЬКО если сам экран отсутствовал в БД (cursor.rowcount > 0).
      Благодаря этому любые переименования и удаления кнопок через /admin сохраняются после перезапуска!
    """
    validate_scenario_graph()

    async with get_db() as db:
        async with db.execute("SELECT value FROM settings WHERE key = 'scenario_version'") as cur:
            row = await cur.fetchone()
            db_version = row[0] if row else ""

        need_full_seed = force or (db_version != CURRENT_SCENARIO_VERSION)

        if need_full_seed:
            print("🔄 Обновляем структуру базовых экранов и кнопок до актуального ТЗ...")
            await db.execute("DELETE FROM buttons")
            await db.execute("DELETE FROM nodes")

        for node in SCENARIO_NODES:
            n_id = node["id"]
            text = node["text"]
            n_type = node.get("type", "regular")
            auto_next = node.get("next_node_id", "")
            b_weight = node.get("budget", 0.0)
            t_days = node.get("days", 0)

            cursor = await db.execute("""
                INSERT OR IGNORE INTO nodes (id, text, node_type, next_node_id, budget_weight, timeline_days)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (n_id, text, n_type, auto_next, b_weight, t_days))

            node_was_created = (cursor.rowcount > 0)

            # Кнопки добавляются только при первом создании экрана или полном сбросе
            if need_full_seed or node_was_created:
                for order_idx, btn in enumerate(node.get("buttons", [])):
                    btn_text = btn.get("text", "")
                    action = btn.get("action", "navigate")
                    target = btn.get("target", "")
                    url = btn.get("url", "")
                    btn_budget = btn.get("budget", 0.0)
                    btn_days = btn.get("days", 0)
                    row_idx = btn.get("row", 0)

                    await db.execute("""
                        INSERT INTO buttons (node_id, text, action_type, target_node_id, url, budget_weight, timeline_days, row_idx, order_idx)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (n_id, btn_text, action, target, url, btn_budget, btn_days, row_idx, order_idx))

        if need_full_seed:
            await db.execute("""
                INSERT INTO settings (key, value) VALUES ('scenario_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (CURRENT_SCENARIO_VERSION,))

        await db.commit()
        print("🎉 Сценарий готов к работе (пользовательские правки CMS защищены от перезаписи)!")
