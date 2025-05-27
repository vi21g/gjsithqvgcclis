import aiosqlite
from pathlib import Path
from typing import List, Dict, Any
import json

from config import MODEL, TEMPERATURE, DEFAULT_SYSTEM_PROMPT

DB_PATH = Path("database") / "bot.db"


class Database:
    def __init__(self):
        self.connection = None

    async def connect(self):
        """Устанавливаем соединение с базой данных"""
        self.connection = await aiosqlite.connect(DB_PATH)
        await self._create_tables()

    async def close(self):
        """Закрываем соединение с базой данных"""
        if self.connection:
            await self.connection.close()

    async def _create_tables(self):
        """Создаем таблицы, если они не существуют"""
        # Создаем таблицу с явными значениями по умолчанию (без параметров)
        await self.connection.execute(f"""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            model TEXT NOT NULL DEFAULT '{MODEL}',
            temperature REAL NOT NULL DEFAULT {TEMPERATURE},
            system_prompt TEXT NOT NULL DEFAULT '{DEFAULT_SYSTEM_PROMPT.replace("'", "''")}'
            )
        """)

        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_settings (user_id)
            )
        """)
        await self.connection.commit()

    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Получаем настройки пользователя"""
        async with self.connection.execute(
                "SELECT model, temperature, system_prompt FROM user_settings WHERE user_id = ?",
                (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if result:
                return {
                    "model": result[0],
                    "temperature": result[1],
                    "system_prompt": result[2]
                }

            # Если пользователя нет, создаем запись с настройками по умолчанию
            await self.connection.execute(
                "INSERT INTO user_settings (user_id) VALUES (?)",
                (user_id,)
            )
            await self.connection.commit()

            return {
                "model": MODEL,
                "temperature": TEMPERATURE,
                "system_prompt": DEFAULT_SYSTEM_PROMPT
            }

    async def update_user_settings(
            self,
            user_id: int,
            model: str = None,
            temperature: float = None,
            system_prompt: str = None
    ) -> None:
        """Обновляем настройки пользователя"""
        updates = []
        params = []

        if model is not None:
            updates.append("model = ?")
            params.append(model)
        if temperature is not None:
            updates.append("temperature = ?")
            params.append(temperature)
        if system_prompt is not None:
            updates.append("system_prompt = ?")
            params.append(system_prompt)

        if updates:
            params.append(user_id)
            query = f"UPDATE user_settings SET {', '.join(updates)} WHERE user_id = ?"
            await self.connection.execute(query, params)
            await self.connection.commit()

    async def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """Получаем историю диалога пользователя"""
        async with self.connection.execute(
                "SELECT role, content FROM conversation_history WHERE user_id = ? ORDER BY timestamp",
                (user_id,)
        ) as cursor:
            return [{"role": row[0], "content": row[1]} for row in await cursor.fetchall()]

    async def add_message_to_history(
            self,
            user_id: int,
            role: str,
            content: str
    ) -> None:
        """Добавляем сообщение в историю диалога"""
        await self.connection.execute(
            "INSERT INTO conversation_history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await self.connection.commit()

    async def clear_conversation_history(self, user_id: int) -> None:
        """Очищаем историю диалога пользователя"""
        await self.connection.execute(
            "DELETE FROM conversation_history WHERE user_id = ?",
            (user_id,)
        )
        await self.connection.commit()


# Создаем экземпляр базы данных для использования в других модулях
db = Database()
