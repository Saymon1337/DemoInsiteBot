import aiosqlite
import logging
from database.db import DB_NAME
from scenario.data import SCENARIO_NODES

logger = logging.getLogger(__name__)

def validate_scenario_graph():
    """Автоматическая валидация графа сценария."""
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
    
    print("✅ Граф сценария полностью валиден! Ошибок нет.")

async def seed_scenario_to_db(force: bool = False):
    """
    Умная синхронизация базы:
    - Если force=True (кнопка сброса к заводским) — полная чистка и перезапись базовых экранов.
    - Если force=False (обычный старт) — восстанавливает недостающие базовые экраны (main_menu и др.) через INSERT OR IGNORE, не затирая созданные админом новые экраны!
    """
    validate_scenario_graph()

    async with aiosqlite.connect(DB_NAME) as db:
        if force:
            print("🔄 ПРИНУДИТЕЛЬНО восстанавливаем все экраны и кнопки...")
            await db.execute("DELETE FROM buttons")
            await db.execute("DELETE FROM nodes")

        # Восстанавливаем базовые экраны, если они были удалены
        for node in SCENARIO_NODES:
            n_id = node["id"]
            text = node["text"]
            n_type = node.get("type", "regular")
            auto_next = node.get("next_node_id", "")
            b_weight = node.get("budget", 0.0)
            t_days = node.get("days", 0)

            await db.execute("""
                INSERT OR IGNORE INTO nodes (id, text, node_type, next_node_id, budget_weight, timeline_days)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (n_id, text, n_type, auto_next, b_weight, t_days))

            for order_idx, btn in enumerate(node.get("buttons", [])):
                btn_text = btn.get("text", "")
                action = btn.get("action", "navigate")
                target = btn.get("target", "")
                url = btn.get("url", "")
                btn_budget = btn.get("budget", 0.0)
                btn_days = btn.get("days", 0)
                row_idx = btn.get("row", 0)

                # Проверяем наличие кнопки перед вставкой
                async with db.execute("SELECT id FROM buttons WHERE node_id = ? AND text = ?", (n_id, btn_text)) as cur:
                    exists = await cur.fetchone()

                if not exists:
                    await db.execute("""
                        INSERT INTO buttons (node_id, text, action_type, target_node_id, url, budget_weight, timeline_days, row_idx, order_idx)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (n_id, btn_text, action, target, url, btn_budget, btn_days, row_idx, order_idx))

        await db.commit()
        print("🎉 Базовые экраны (включая main_menu) и кнопки проверены и восстановлены!")