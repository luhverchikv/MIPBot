from dataclasses import dataclass
from environs import Env
from typing import List


@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    owner_id: int


@dataclass
class Config:
    bot: TgBot


# Инициализация Env
env = Env()
env.read_env()  # Читаем из .env файла в корне проекта


# Создаем конфиг
config = Config(
    bot=TgBot(
        token=env('BOT_TOKEN'),
        admin_ids=list(map(int, env.list('ADMIN_IDS'))),
        owner_id=env.int('OWNER_ID')
    ),
)