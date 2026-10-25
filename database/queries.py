import aiosqlite
import json
import time
from config import OWNER_ID
from database.db import DB_NAME
from scenario.data import SCENARIO_NODES


def safe_json_loads(data: str, default=None):
    if not data:
        return default if default is not None else {}
    try:
        return json.loads(data)
    except Exception:
        return default if default is not None else {}


async def ensure_users_schema(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT DEFAULT '',
            saved_name TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            role TEXT DEFAULT 'client',
            role_title TEXT DEFAULT 'Менеджер',
            can_leads INTEGER DEFAULT 1,
            can_calc INTEGER DEFAULT 0,
            can_content INTEGER DEFAULT 0,
            can_broadcast INTEGER DEFAULT 0,
            can_export INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for col, cdef in [
        ("role_title", "TEXT DEFAULT 'Менеджер'"),
        ("can_leads", "INTEGER DEFAULT 1"),
        ("can_calc", "INTEGER DEFAULT 0"),
        ("can_content", "INTEGER DEFAULT 0"),
        ("can_broadcast", "INTEGER DEFAULT 0"),
        ("can_export", "INTEGER DEFAULT 1")
    ]:
        try:
            await db.execute(f"ALTER TABLE users ADD COLUMN {col} {cdef}")
        except Exception:
            pass
    await db.commit()


# --- Настройки ---

async def get_text(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default


async def set_text(key: str, value: str):
    old_value = await get_text(key)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS button_history (
                btn_key TEXT,
                old_text TEXT,
                PRIMARY KEY (btn_key, old_text)
            )
        """)
        if old_value and old_value != value and key.startswith("btn_"):
            await db.execute("INSERT OR IGNORE INTO button_history (btn_key, old_text) VALUES (?, ?)", (key, old_value))

        await db.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))
        await db.commit()


async def get_setting(key: str, default: str = "") -> str:
    return await get_text(key, default)


async def set_setting(key: str, value: str):
    await set_text(key, value)


# --- Пользователи, Роли и Разрешения ---

async def add_or_update_user(tg_id: int, username: str, full_name: str, default_role: str = 'client'):
    clean_un = (username or "").strip().lstrip('@').lower()
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        if clean_un:
            async with db.execute("SELECT * FROM users WHERE LOWER(LTRIM(username, '@')) = ?", (clean_un,)) as cur:
                rows = [dict(r) for r in await cur.fetchall()]
            staff_row = next((r for r in rows if r.get("role") in ("staff", "owner")), None)
            if staff_row:
                await db.execute("DELETE FROM users WHERE LOWER(LTRIM(username, '@')) = ? AND id != ?", (clean_un, staff_row["id"]))
                await db.execute("UPDATE users SET tg_id = ?, username = ?, full_name = ? WHERE id = ?", (tg_id, clean_un, full_name or "", staff_row["id"]))
                await db.commit()
                return

        await db.execute("""
            INSERT INTO users (tg_id, username, full_name, role) VALUES (?, ?, ?, ?)
            ON CONFLICT(tg_id) DO UPDATE SET 
                username = CASE WHEN excluded.username != '' THEN excluded.username ELSE users.username END,
                full_name = CASE WHEN excluded.full_name != '' THEN excluded.full_name ELSE users.full_name END
        """, (tg_id, clean_un, full_name or "", default_role))
        await db.commit()


async def get_user_permissions(user_id: int, username: str = "") -> dict:
    if user_id == OWNER_ID:
        return {
            "is_owner": True, "is_staff": True, "role_title": "Владелец агентства",
            "can_leads": True, "can_calc": True, "can_content": True, "can_broadcast": True, "can_export": True
        }
    clean_un = (username or "").strip().lstrip('@').lower()
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        row = None
        async with db.execute("SELECT * FROM users WHERE tg_id = ? AND role IN ('staff', 'owner')", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row and clean_un:
            async with db.execute("SELECT * FROM users WHERE LOWER(LTRIM(username, '@')) = ? AND role IN ('staff', 'owner')", (clean_un,)) as cur:
                row = await cur.fetchone()
                if row:
                    await db.execute("DELETE FROM users WHERE tg_id = ? AND id != ?", (user_id, row["id"]))
                    await db.execute("UPDATE users SET tg_id = ? WHERE id = ?", (user_id, row["id"]))
                    await db.commit()
        if not row:
            return {"is_owner": False, "is_staff": False}
        u = dict(row)
        return {
            "is_owner": (u.get("role") == "owner"), "is_staff": True,
            "role_title": u.get("role_title") or "Менеджер",
            "can_leads": bool(u.get("can_leads", 1)), "can_calc": bool(u.get("can_calc", 0)),
            "can_content": bool(u.get("can_content", 0)), "can_broadcast": bool(u.get("can_broadcast", 0)),
            "can_export": bool(u.get("can_export", 1))
        }


async def set_user_role_by_username(username_or_id: str, role: str = 'staff', role_title: str = 'Менеджер') -> int:
    clean = username_or_id.strip().lstrip('@')
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        if clean.isdigit():
            tg_val = int(clean)
            async with db.execute("SELECT id FROM users WHERE tg_id = ?", (tg_val,)) as cur:
                row = await cur.fetchone()
            if row:
                await db.execute("UPDATE users SET role = ?, role_title = ? WHERE id = ?", (role, role_title, row["id"]))
                await db.commit()
                return row["id"]
            cur = await db.execute("INSERT INTO users (tg_id, username, role, role_title, can_leads, can_export) VALUES (?, ?, ?, ?, 1, 1)", (tg_val, f"id_{tg_val}", role, role_title))
            await db.commit()
            return cur.lastrowid
        else:
            clean_low = clean.lower()
            async with db.execute("SELECT id, tg_id FROM users WHERE LOWER(LTRIM(username, '@')) = ?", (clean_low,)) as cur:
                rows = await cur.fetchall()
            if rows:
                target_id = next((r["id"] for r in rows if r["tg_id"]), rows[0]["id"])
                await db.execute("DELETE FROM users WHERE LOWER(LTRIM(username, '@')) = ? AND id != ?", (clean_low, target_id))
                await db.execute("""
                    UPDATE users SET username = ?, role = ?, role_title = ? WHERE id = ?
                """, (clean_low, role, role_title, target_id))
                await db.commit()
                return target_id
            cur = await db.execute("INSERT INTO users (username, role, role_title, can_leads, can_export) VALUES (?, ?, ?, 1, 1)", (clean_low, role, role_title))
            await db.commit()
            return cur.lastrowid


async def apply_staff_role_preset(db_user_id: int, preset_key: str):
    presets = {
        "sales": ("👨‍💼 Менеджер продаж", 1, 0, 0, 0, 1),
        "editor": ("✍️ Контент-редактор", 0, 0, 1, 1, 0),
        "estimator": ("🧮 Сметчик-аналитик", 1, 1, 0, 0, 1),
        "super": ("👑 Управляющий (Все права)", 1, 1, 1, 1, 1)
    }
    if preset_key not in presets:
        return
    title, leads, calc, content, bcast, exp = presets[preset_key]
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        await db.execute("""
            UPDATE users SET role_title = ?, can_leads = ?, can_calc = ?, can_content = ?, can_broadcast = ?, can_export = ? WHERE id = ?
        """, (title, leads, calc, content, bcast, exp, db_user_id))
        await db.commit()


async def toggle_staff_permission(db_user_id: int, perm_key: str):
    if perm_key not in {"can_leads", "can_calc", "can_content", "can_broadcast", "can_export"}:
        return
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        await db.execute(f"UPDATE users SET {perm_key} = CASE WHEN {perm_key} = 1 THEN 0 ELSE 1 END WHERE id = ?", (db_user_id,))
        await db.commit()


async def get_all_staff() -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE role IN ('owner', 'staff') OR tg_id = ? ORDER BY id ASC", (OWNER_ID,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]


async def get_staff_by_db_id(db_id: int) -> dict | None:
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", (db_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_staff_and_owner_ids() -> list[int]:
    staff = await get_all_staff()
    ids = {OWNER_ID}
    for s in staff:
        if s.get("tg_id") and s.get("can_leads", 1):
            ids.add(s["tg_id"])
    return list(ids)


async def get_user_profile(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT saved_name, phone FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def save_user_profile(tg_id: int, saved_name: str, phone: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        await db.execute("INSERT INTO users (tg_id, saved_name, phone) VALUES (?, ?, ?) ON CONFLICT(tg_id) DO UPDATE SET saved_name = excluded.saved_name, phone = excluded.phone", (tg_id, saved_name, phone))
        await db.commit()


async def get_user_role(user_id: int) -> str:
    if user_id == OWNER_ID:
        return 'owner'
    async with aiosqlite.connect(DB_NAME) as db:
        await ensure_users_schema(db)
        async with db.execute("SELECT role FROM users WHERE tg_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'client'


async def get_all_users_by_target(target: str = "all") -> list[int]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM user_sessions") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows if r[0]] or [OWNER_ID]


# --- КОНСТРУКТОР ЭКРАНОВ, ПОРЯДОК, БЭКАП И ВОССТАНОВЛЕНИЕ ---

async def get_node(node_id: str) -> dict | None:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_all_nodes_list() -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, text, node_type FROM nodes ORDER BY id ASC") as cursor:
            return [dict(r) for r in await cursor.fetchall()]


async def create_custom_node(text: str, node_type: str = 'regular', next_node_id: str = 'main_menu') -> str:
    new_node_id = f"custom_{int(time.time())}"
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO nodes (id, text, node_type, next_node_id, budget_weight, timeline_days)
            VALUES (?, ?, ?, ?, 0.0, 0)
        """, (new_node_id, text, node_type, next_node_id))
        await db.execute("""
            INSERT INTO buttons (node_id, text, action_type, target_node_id, url, row_idx, order_idx)
            VALUES (?, '⬅️ Назад', 'back', '', '', 99, 0)
        """, (new_node_id,))
        await db.commit()
    return new_node_id


async def delete_custom_node(node_id: str) -> tuple[bool, str]:
    """Защищает все базовые экраны сценария от удаления (удалять можно только созданные через CMS custom_* экраны)."""
    protected = {n["id"] for n in SCENARIO_NODES}
    if node_id in protected:
        return False, "Это базовый экран сценария, его нельзя удалить (вы можете изменить его текст или кнопки)."
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM buttons WHERE node_id = ? OR target_node_id = ?", (node_id, node_id))
        await db.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        await db.commit()
    return True, "Кастомный экран удален."


async def export_scenario_json() -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM nodes") as c1:
            nodes = [dict(r) for r in await c1.fetchall()]
        async with db.execute("SELECT * FROM buttons ORDER BY row_idx ASC, order_idx ASC") as c2:
            buttons = [dict(r) for r in await c2.fetchall()]
    for n in nodes:
        n["buttons"] = [b for b in buttons if b["node_id"] == n["id"]]
    return json.dumps(nodes, ensure_ascii=False, indent=2)


async def import_scenario_json(json_str: str) -> tuple[bool, str]:
    try:
        data = json.loads(json_str)
        if not isinstance(data, list) or not data:
            return False, "Файл не содержит корректного списка экранов (nodes)."

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("DELETE FROM buttons")
            await db.execute("DELETE FROM nodes")

            for node in data:
                n_id = node.get("id")
                if not n_id:
                    continue
                text = node.get("text", "")
                n_type = node.get("node_type", "regular")
                media = node.get("media_file_id", "")
                auto_next = node.get("next_node_id", "")
                b_weight = float(node.get("budget_weight", 0.0))
                t_days = int(node.get("timeline_days", 0))

                await db.execute("""
                    INSERT INTO nodes (id, text, node_type, media_file_id, next_node_id, budget_weight, timeline_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (n_id, text, n_type, media, auto_next, b_weight, t_days))

                for b in node.get("buttons", []):
                    b_text = b.get("text", "")
                    action = b.get("action_type", "navigate")
                    target = b.get("target_node_id", "")
                    url = b.get("url", "")
                    btn_b = float(b.get("budget_weight", 0.0))
                    btn_d = int(b.get("timeline_days", 0))
                    row_idx = int(b.get("row_idx", 0))
                    order_idx = int(b.get("order_idx", 0))

                    await db.execute("""
                        INSERT INTO buttons (node_id, text, action_type, target_node_id, url, budget_weight, timeline_days, row_idx, order_idx)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (n_id, b_text, action, target, url, btn_b, btn_d, row_idx, order_idx))

            await db.commit()
        return True, f"Успешно восстановлено экранов: {len(data)}"
    except Exception as e:
        return False, f"Ошибка при разборе бэкапа: {e}"


async def get_node_buttons(node_id: str) -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM buttons WHERE node_id = ? ORDER BY row_idx ASC, order_idx ASC, id ASC", (node_id,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]


async def get_button_by_id(btn_id: int) -> dict | None:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM buttons WHERE id = ?", (btn_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def move_button_to_position(btn_id: int, new_pos_1based: int) -> tuple[bool, int, int]:
    btn = await get_button_by_id(btn_id)
    if not btn:
        return False, 0, 0
    node_id = btn["node_id"]
    buttons = await get_node_buttons(node_id)
    content_btns = [b for b in buttons if b.get("action_type") != "back"]
    back_btns = [b for b in buttons if b.get("action_type") == "back"]

    cur_idx = next((i for i, b in enumerate(content_btns) if b["id"] == btn_id), None)
    if cur_idx is None:
        return False, 0, 0

    old_pos = cur_idx + 1
    target_idx = max(0, min(new_pos_1based - 1, len(content_btns) - 1))

    item = content_btns.pop(cur_idx)
    content_btns.insert(target_idx, item)

    async with aiosqlite.connect(DB_NAME) as db:
        for idx, b in enumerate(content_btns):
            await db.execute("UPDATE buttons SET row_idx = ?, order_idx = 0 WHERE id = ?", (idx, b["id"]))
        for b in back_btns:
            await db.execute("UPDATE buttons SET row_idx = 99, order_idx = 0 WHERE id = ?", (b["id"],))
        await db.commit()

    return True, old_pos, target_idx + 1


async def swap_button_step(btn_id: int, direction: str) -> bool:
    btn = await get_button_by_id(btn_id)
    if not btn:
        return False
    buttons = await get_node_buttons(btn["node_id"])
    content_btns = [b for b in buttons if b.get("action_type") != "back"]
    cur_idx = next((i for i, b in enumerate(content_btns) if b["id"] == btn_id), None)
    if cur_idx is None:
        return False
    target_pos = (cur_idx) if direction == "up" else (cur_idx + 2)
    ok, _, _ = await move_button_to_position(btn_id, target_pos)
    return ok


async def update_button_text(btn_id: int, new_text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE buttons SET text = ? WHERE id = ?", (new_text, btn_id))
        await db.commit()


async def update_button_target(btn_id: int, action_type: str, target_val: str):
    url = target_val if action_type == "url" else ""
    target_node = target_val if action_type == "navigate" else ""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE buttons SET action_type = ?, target_node_id = ?, url = ? WHERE id = ?", (action_type, target_node, url, btn_id))
        await db.commit()


async def update_button_weights(btn_id: int, budget_weight: float, timeline_days: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE buttons SET budget_weight = ?, timeline_days = ? WHERE id = ?", (budget_weight, timeline_days, btn_id))
        await db.commit()


async def update_node_text(node_id: str, new_text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE nodes SET text = ? WHERE id = ?", (new_text, node_id))
        await db.commit()


async def add_button(node_id: str, text: str, action_type: str, target_node_id: str = '', url: str = '', budget_weight: float = 0.0, timeline_days: int = 0, row_idx: int = None):
    if row_idx is None:
        buttons = await get_node_buttons(node_id)
        content_btns = [b for b in buttons if b.get("action_type") != "back"]
        row_idx = len(content_btns)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO buttons (node_id, text, action_type, target_node_id, url, budget_weight, timeline_days, row_idx)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (node_id, text, action_type, target_node_id, url, budget_weight, timeline_days, row_idx))
        await db.commit()


async def delete_button(button_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM buttons WHERE id = ?", (button_id,))
        await db.commit()


# --- Сессии и Стек истории ---

async def get_or_create_session(user_id: int) -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM user_sessions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        if not row:
            await db.execute("INSERT INTO user_sessions (user_id) VALUES (?)", (user_id,))
            await db.commit()
            return {"user_id": user_id, "current_node_id": "privacy_block", "history": [], "answers": {}, "multiselect": []}
        data = dict(row)
        return {
            "user_id": user_id,
            "current_node_id": data.get("current_node_id", "privacy_block"),
            "history": safe_json_loads(data.get("history_json"), default=[]),
            "answers": safe_json_loads(data.get("answers_json"), default={}),
            "multiselect": safe_json_loads(data.get("multiselect_json"), default=[])
        }


async def update_session_node(user_id: int, new_node_id: str, push_history: bool = True):
    session = await get_or_create_session(user_id)
    history = session["history"]
    if push_history and session["current_node_id"] and session["current_node_id"] != new_node_id:
        history.append(session["current_node_id"])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE user_sessions SET current_node_id = ?, history_json = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (new_node_id, json.dumps(history, ensure_ascii=False), user_id)
        )
        await db.commit()


async def pop_session_history(user_id: int) -> str:
    """Возвращает предыдущий экран из стека и очищает начисленные веса покинутого шага."""
    session = await get_or_create_session(user_id)
    history = session["history"]
    current_node_id = session.get("current_node_id", "")
    prev_node_id = history.pop() if history else "main_menu"

    answers = session.get("answers", {})
    node_budgets = answers.get("_node_budgets", {})
    node_days = answers.get("_node_days", {})

    for n_id in (current_node_id, prev_node_id):
        if isinstance(node_budgets, dict):
            node_budgets.pop(n_id, None)
        if isinstance(node_days, dict):
            node_days.pop(n_id, None)

    answers["_node_budgets"] = node_budgets
    answers["_node_days"] = node_days

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE user_sessions SET current_node_id = ?, history_json = ?, answers_json = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (prev_node_id, json.dumps(history, ensure_ascii=False), json.dumps(answers, ensure_ascii=False), user_id)
        )
        await db.commit()
    return prev_node_id


async def toggle_multiselect_option(user_id: int, node_id: str, option_text: str) -> list[str]:
    session = await get_or_create_session(user_id)
    answers = session["answers"]
    selected = answers.get(node_id, [])
    if not isinstance(selected, list):
        selected = []

    def is_exclusive(txt: str) -> bool:
        t = txt.strip().lower()
        if t in ("нет", "❌ нет"):
            return True
        return any(ex in t for ex in [
            "пока нет сайта",
            "не знаю, нужна рекомендация",
            "нет вариаций",
            "нет, никогда не обращались",
            "нет, пока не продвигаем",
            "никогда не продвигали",
            "затрудняюсь"
        ])

    if is_exclusive(option_text):
        selected = [] if option_text in selected else [option_text]
    else:
        selected = [x for x in selected if not is_exclusive(x)]
        if option_text in selected:
            selected.remove(option_text)
        else:
            selected.append(option_text)

    answers[node_id] = selected
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE user_sessions 
            SET answers_json = ?, 
                multiselect_json = ? 
            WHERE user_id = ?
        """, (json.dumps(answers, ensure_ascii=False), json.dumps(selected, ensure_ascii=False), user_id))
        await db.commit()
    return selected


async def save_session_answer(user_id: int, key: str, value):
    session = await get_or_create_session(user_id)
    answers = session["answers"]
    answers[key] = value
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE user_sessions SET answers_json = ? WHERE user_id = ?", (json.dumps(answers, ensure_ascii=False), user_id))
        await db.commit()


async def reset_session(user_id: int, keep_privacy: bool = True):
    session = await get_or_create_session(user_id)
    answers = {}
    if keep_privacy and session.get("answers", {}).get("_privacy_accepted"):
        answers["_privacy_accepted"] = True
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE user_sessions 
            SET current_node_id = 'main_menu', 
                history_json = '[]', 
                answers_json = ?, 
                multiselect_json = '[]', 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        """, (json.dumps(answers, ensure_ascii=False), user_id))
        await db.commit()


# --- Заявки и CRM ---

async def create_lead(user_id: int, username: str, client_name: str, client_phone: str, messenger: str, preferred_time: str, branch: str, tz_file_id: str, answers_summary: str, budget_estimate: str) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT MAX(id) FROM leads") as cursor:
            row = await cursor.fetchone()
            last_id = row[0] or 0
            lead_code = f"#{(last_id % 999) + 1:03d}"
        await db.execute("""
            INSERT INTO leads (lead_code, user_id, username, client_name, client_phone, messenger, preferred_time, branch, tz_file_id, answers_summary, budget_estimate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lead_code, user_id, username or "", client_name, client_phone, messenger, preferred_time, branch, tz_file_id, answers_summary, budget_estimate))
        await db.commit()
        return lead_code


async def get_all_leads(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]


async def get_lead_by_code(lead_code: str) -> dict | None:
    clean_code = lead_code if lead_code.startswith("#") else f"#{lead_code}"
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM leads WHERE lead_code = ?", (clean_code,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_lead_status(lead_code: str, status: str, manager_name: str = ""):
    clean_code = lead_code if lead_code.startswith("#") else f"#{lead_code}"
    async with aiosqlite.connect(DB_NAME) as db:
        if manager_name:
            await db.execute("UPDATE leads SET status = ?, manager_name = ? WHERE lead_code = ?", (status, manager_name, clean_code))
        else:
            await db.execute("UPDATE leads SET status = ? WHERE lead_code = ?", (status, clean_code))
        await db.commit()
