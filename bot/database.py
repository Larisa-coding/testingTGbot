import asyncpg
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

pool = None

async def create_table():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id SERIAL PRIMARY KEY,
                telegram_user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                phone_number VARCHAR(20),
                registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_sent BOOLEAN DEFAULT FALSE
            )
        """)

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id SERIAL PRIMARY KEY,
                telegram_user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                phone_number VARCHAR(20),
                registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_sent BOOLEAN DEFAULT FALSE
            )
        """)

async def add_participant(user_id, username, phone):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO participants (telegram_user_id, username, phone_number)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_user_id) DO NOTHING
        """, user_id, username, phone)

async def get_all_participants():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM participants")

async def get_unnotified_participants():
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT telegram_user_id FROM participants 
            WHERE reminder_sent = FALSE
        """)

async def mark_reminder_sent(user_id):
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE participants SET reminder_sent = TRUE
            WHERE telegram_user_id = $1
        """, user_id)

async def get_participant_count():
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT COUNT(*) FROM participants")
        return result

async def broadcast_message():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT telegram_user_id FROM participants")