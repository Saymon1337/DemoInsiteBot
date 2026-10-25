import asyncio
import aiosqlite
from contextlib import asynccontextmanager

DB_NAME = "agency.db"

_db_conn: aiosqlite.Connection | None = None
_db_lock = asyncio.Lock()


@asynccontextmanager
async def get_db():
    """
    Единое постоянное соединение с SQLite в режиме WAL с асинхронной очередью.
    Создает ровно 1 поток на всё время работы бота — полностью исключает зависание хоста.
    """
    global _db_conn
    async with _db_lock:
        if _db_conn is None:
            _db_conn = await aiosqlite.connect(DB_NAME, timeout=30.0)
            _db_conn.row_factory = aiosqlite.Row
            await _db_conn.execute("PRAGMA journal_mode=WAL")
            await _db_conn.execute("PRAGMA synchronous=NORMAL")
            await _db_conn.execute("PRAGMA busy_timeout=15000")
            await _db_conn.commit()
        yield _db_conn


async def close_db():
    """Корректное закрытие соединения при остановке бота."""
    global _db_conn
    async with _db_lock:
        if _db_conn is not None:
            await _db_conn.close()
            _db_conn = None


async def init_db():
    """Создание таблиц и однократная миграция при старте бота."""
    async with get_db() as db:
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

        await db.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                node_type TEXT DEFAULT 'regular',
                media_file_id TEXT DEFAULT '',
                next_node_id TEXT DEFAULT '',
                budget_weight REAL DEFAULT 0.0,
                timeline_days INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL,
                text TEXT NOT NULL,
                action_type TEXT DEFAULT 'navigate',
                target_node_id TEXT DEFAULT '',
                url TEXT DEFAULT '',
                budget_weight REAL DEFAULT 0.0,
                timeline_days INTEGER DEFAULT 0,
                row_idx INTEGER DEFAULT 0,
                order_idx INTEGER DEFAULT 0,
                FOREIGN KEY (node_id) REFERENCES nodes (id) ON DELETE CASCADE
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id INTEGER PRIMARY KEY,
                current_node_id TEXT DEFAULT 'privacy_block',
                history_json TEXT DEFAULT '[]',
                answers_json TEXT DEFAULT '{}',
                multiselect_json TEXT DEFAULT '[]',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_code TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT DEFAULT '',
                client_name TEXT NOT NULL,
                client_phone TEXT NOT NULL,
                messenger TEXT DEFAULT '',
                preferred_time TEXT DEFAULT '',
                branch TEXT DEFAULT '',
                tz_file_id TEXT DEFAULT '',
                answers_summary TEXT DEFAULT '',
                budget_estimate TEXT DEFAULT '',
                status TEXT DEFAULT 'new',
                manager_name TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS button_history (
                btn_key TEXT,
                old_text TEXT,
                PRIMARY KEY (btn_key, old_text)
            )
        """)
        await db.commit()

        user_cols = [
            ("role_title", "TEXT DEFAULT 'Менеджер'"),
            ("can_leads", "INTEGER DEFAULT 1"),
            ("can_calc", "INTEGER DEFAULT 0"),
            ("can_content", "INTEGER DEFAULT 0"),
            ("can_broadcast", "INTEGER DEFAULT 0"),
            ("can_export", "INTEGER DEFAULT 1")
        ]
        for col, cdef in user_cols:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col} {cdef}")
                await db.commit()
            except Exception:
                pass

        default_settings = [
            ('leads_channel_id', ''),
            ('leads_channel_title', ''),
            ('leads_routing_mode', 'both'),
            ('agency_telegram', '@site_it'),
            ('agency_phone', '+7 999 155-10-43'),
            ('agency_email', 'site-it@mail.ru'),
            ('calc_base_landing', '40000'),
            ('calc_base_multipage', '80000'),
            ('calc_base_promo', '35000')
        ]
        for k, v in default_settings:
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

        await db.commit()
