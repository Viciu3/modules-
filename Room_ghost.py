__version__ = (7, 0, 0)
# meta developer: @Shadow_red1

from telethon import events
from .. import loader, utils
import asyncio
import requests

@loader.tds
class Room_ghost(loader.Module):
    """Автокомнаты от Тени! настройка в кфг.)"""

    strings = {"name": "Ghost-room"}

    def __init__(self):
        self.allowed_users = set()  # Множество для хранения разрешенных пользователей
        self.repo_url = "https://raw.githubusercontent.com/Viciu3/modules-/main/allowed_users.json"  # URL для загрузки разрешенных пользователей
        self.module_url = "https://raw.githubusercontent.com/Viciu3/modules-/main/Room_ghost.py"  # URL для обновления модуля
        self.trigger_active = False  # Переменная для отслеживания активного триггера

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        await self.load_allowed_users()  # Загружаем разрешенных пользователей при инициализации

        @self.client.on(events.NewMessage(from_users='@bfgbunker_bot'))
        async def trigger_handler(event):
            if "в бункере произошёл пожар" in event.raw_text or "в бункере произошёл потоп" in event.raw_text:
                if not self.trigger_active:
                    self.trigger_active = True
                    for _ in range(3):
                        await event.respond("Починить бункер")
                        await asyncio.sleep(3)  # 3 секунды между сообщениями

                    # Ждем ответа от бота о том, что происшествие исправлено
                    response = await self.client.wait_for(
                        events.NewMessage(from_users='@bfgbunker_bot'),
                        timeout=30  # Ждем максимум 30 секунд
                    )
                    if "ты успешно исправил(-а) происшествие" in response.raw_text:
                        self.trigger_active = False  

    async def load_allowed_users(self):
        """Загружает список разрешенных пользователей с GitHub."""
        try:
            response = requests.get(self.repo_url)
            if response.status_code == 200:
                data = response.json()
                self.allowed_users = set(data.get("allowed_users", []))
            else:
                print("Не удалось загрузить список разрешенных пользователей.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке пользователей: {str(e)}")

    @loader.command()
    async def updatecmd(self, message):
        """Команда для обновления модуля с GitHub."""
        user_id = message.from_user.id
        if user_id not in self.allowed_users:
            await message.edit("<b>У вас нет доступа к этой команде.</b>")
            return

        try:
            response = requests.get(self.module_url)
            if response.status_code == 200:
                with open(__file__, 'w', encoding='utf-8') as module_file:  # Обновляем текущий файл модуля
                    module_file.write(response.text)
                await message.edit("<b>Модуль успешно обновлён!</b>")
            else:
                await message.edit("<b>Не удалось получить обновления.</b>")
        except Exception as e:
            await message.edit(f"<b>Произошла ошибка:</b> {str(e)}")

    async def ghostoncmd(self, message):
        """Используйте .ghoston <интервал в секундах> для начала кликов."""
        user_id = message.from_user.id
        if user_id not in self.allowed_users:
            await message.edit("<b>У вас нет доступа к этой команде.</b>")
            return

        if not message.is_reply:
            await message.edit('<b>Нету реплая.</b>')
            return

        args = utils.get_args_raw(message)
        try:
            interval = float(args)
        except ValueError:
            interval = 1.5  # Значение по умолчанию
        
        self.clicker = True
        await message.edit(f'<b>Кликер включен. Интервал: {interval} секунд.</b>')
        
        while self.clicker:
            reply = await message.get_reply_message()
            if reply and reply.buttons:
                row_index = self.config["button_row_index"]
                column_index = self.config["button_column_index"]
                if row_index < len(reply.buttons) and column_index < len(reply.buttons[row_index]):
                    button = reply.buttons[row_index][column_index]
                    await button.click()
                    await asyncio.sleep(interval)
                else:
                    await message.edit('<b>Указанный индекс кнопки вне диапазона.</b>')
                    self.clicker = False
                    break
            else:
                await message.edit('<b>В сообщении нет инлайн кнопок для нажатия.</b>')
                self.clicker = False
                break

    async def ghostoffcmd(self, message):
        """Используйте .ghostoff для остановки кликера."""
        user_id = message.from_user.id
        if user_id not in self.allowed_users:
            await message.edit("<b>У вас нет доступа к этой команде.</b>")
            return

        self.clicker = False
        await message.edit('<b>Кликер выключен.</b>')

    async def ghostinfocmd(self, message):
        """Используйте .ghostinfo для получения информации о режимах и интервалах также комбинацыи нажатия."""
        user_id = message.from_user.id
        if user_id not in self.allowed_users:
            await message.edit("<b>У вас нет доступа к этой команде.</b>")
            return

        info_message = (
            "[row] [column] кфг настройка!\n"
            "[ 0 ] [ 0 ] это режим за кр.\n"
            "[ 0 ] [ 1 ] это режим за бут.\n"
            "[ 1 ] [ 0 ] это +1 интервал 1s\n"
            "[ 1 ] [ 1 ] это +5 интервал 1s\n"
            "[ 2 ] [ 0 ] это +20 интервал 60s\n"
            "[ 2 ] [ 1 ] это +100 интервал 120s\n"
            "[ 3 ] [ 0 ] это +1000 интервал 180s\n"
            "[ 4 ] [ 0 ] это +5000 интервал 180s"
        )
        await message.edit(info_message)
