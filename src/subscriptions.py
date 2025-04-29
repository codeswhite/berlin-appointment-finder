import asyncpg
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

DB_DSN = os.getenv("DATABASE_URL") or (
    f"postgresql://{os.getenv('POSTGRES_USER','burgersucher')}:{os.getenv('POSTGRES_PASSWORD','burgersucher')}@{os.getenv('POSTGRES_HOST','postgres')}:{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','burgersucher')}"
)

class SubscriptionDB:
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = DB_DSN
        self.pool = None
        print("SubscriptionDB initialized")

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def setup(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id BIGINT PRIMARY KEY,
                    date_from DATE,
                    date_to DATE
                )''')

    async def upsert_subscription(self, user_id: int, date_from: Optional[str], date_to: Optional[str]):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO subscriptions (user_id, date_from, date_to)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET date_from = $2, date_to = $3
            ''', user_id, date_from, date_to)

    async def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM subscriptions WHERE user_id = $1
            ''', user_id)
            return dict(rows[0]) if rows else None

    async def get_all_active_subscriptions(self) -> List[Dict]:
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM subscriptions
            ''')
            return [dict(row) for row in rows]

    async def set_dates(self, user_id: int, date_from: Optional[str], date_to: Optional[str]):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE subscriptions SET date_from = $2, date_to = $3 WHERE user_id = $1
            ''', user_id, date_from, date_to)

    async def delete_subscription(self, user_id: int):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM subscriptions WHERE user_id = $1
            ''', user_id)
