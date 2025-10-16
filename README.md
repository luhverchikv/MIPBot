# 🤖 MedInterPlastBot

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**MedInterPlastBot** — телеграм-бот, предназначенный для сбора обратной связи и пожеланий.

---

## ✨ Возможности

- 📩 Сбор **анонимных отзывов**
- 💬 Ответ на **анонимный отзыв**
- 📢 **Рассылка сообщений** пользователям

---

## 📋 Требования

- **Python** 3.12 или выше  
- Установленные зависимости (см. `requirements.txt`)

---

## 🧰 Подготовка сервера

Перед установкой рекомендуется подготовить сервер для работы бота.

### 1. Обновите систему

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Создайте отдельного пользователя (например, `botuser`)

```bash
sudo adduser botuser
```

Добавьте ему права на выполнение команд через `sudo`:

```bash
sudo usermod -aG sudo botuser
```

Переключитесь на нового пользователя:

```bash
su - botuser
```

### 3. Проверьте наличие Python

```bash
python3 --version
```

Если Python не установлен — установите его вместе с менеджером пакетов `pip`:

```bash
sudo apt install -y python3 python3-pip python3-venv
```

Теперь сервер готов к установке бота 👇

---

## 🚀 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/luhverchikv/MIPBot.git
````

### 2. Переход в директорию проекта

```bash
cd MIPBot/
```

### 3. Создание виртуального окружения

```bash
python -m venv .venv
```

### 4. Активация виртуального окружения

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 5. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 6. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```bash
touch .env
```

Внесите в него данные, используя шаблон `.env.example` и сохраните изменения:

```
sudo nano .env
```

### 7. Запуск бота вручную

Находясь в активированном виртуальном окружении:

```bash
python main.py
```

Проверьте, что бот работает корректно и выполните остановку:

```bash
Ctrl+C
```

---

## ⚙️ Настройка автозапуска через systemd

### 1. Создайте сервисный файл

```bash
sudo nano /etc/systemd/system/mip_bot.service
```

Вставьте следующее содержимое (замените пути и имя пользователя на свои):

```ini
[Unit]
Description=MedInterPlast Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/home/your_username/MIPBot
ExecStart=/home/your_username/MIPBot/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Пояснения:**
>
> * `User=` — ваш системный пользователь
> * `WorkingDirectory=` — путь к проекту
> * `ExecStart=` — путь к Python и файлу запуска
> * `Restart=always` — бот будет автоматически перезапускаться при сбоях

Сохраните и выйдите: **Ctrl+O → Enter → Ctrl+X**

---

### 2. Перезагрузка и активация сервиса

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable mip_bot.service
sudo systemctl start mip_bot.service
```

---

### 3. Проверка статуса

```bash
sudo systemctl status mip_bot.service
```

Если всё работает — увидите строку:

```
Active: active (running)
```

---

### 4. Просмотр логов

```bash
journalctl -u mip_bot.service -f
```

(Чтобы выйти из логов, нажмите **Ctrl+C**)

---
| Действие                | Команда                                  |
| ----------------------- | ---------------------------------------- |
| 🛑 Остановить бота      | `sudo systemctl stop mip_bot.service`    |
| 🔁 Перезапустить бота   | `sudo systemctl restart mip_bot.service` |
| 🚫 Отключить автозапуск | `sudo systemctl disable mip_bot.service` |
| ✅ Включить автозапуск   | `sudo systemctl enable mip_bot.service`  |
| 🔍 Проверить статус     | `sudo systemctl status mip_bot.service`  |
| 📜 Просмотреть логи     | `journalctl -u mip_bot.service -f`       |

---

