from pathlib import Path

import aiosqlite

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
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            model TEXT,
            temperature REAL,
            system_prompt TEXT
        )
        """)
        await self.connection.commit()

    async def get_user_settings(self, user_id: int) -> dict:
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
            return None

    async def update_user_settings(
            self,
            user_id: int,
            model: str = None,
            temperature: float = None,
            system_prompt: str = None
    ) -> None:
        """Обновляем настройки пользователя"""
        # Сначала проверяем, есть ли запись для этого пользователя
        current_settings = await self.get_user_settings(user_id)

        if current_settings is None:
            # Если записи нет, создаем новую
            await self.connection.execute(
                """
                INSERT INTO user_settings (user_id, model, temperature, system_prompt)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, model, temperature, system_prompt)
            )
        else:
            # Если запись есть, обновляем только переданные параметры
            update_model = model if model is not None else current_settings["model"]
            update_temp = temperature if temperature is not None else current_settings["temperature"]
            update_prompt = system_prompt if system_prompt is not None else current_settings["system_prompt"]

            await self.connection.execute(
                """
                UPDATE user_settings
                SET model = ?, temperature = ?, system_prompt = ?
                WHERE user_id = ?
                """,
                (update_model, update_temp, update_prompt, user_id)
            )

        await self.connection.commit()


# Создаем экземпляр базы данных для использования в других модулях
db = Database()
