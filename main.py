import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, Message
)
from aiogram.utils.markdown import hbold, hitalic

from config import (
    TOKEN, EVENT_NAME, EVENT_DATE, EVENT_LOCATION, EVENT_ADDRESS,
    RESPONSE_TEXTS, REGISTRATION_LINKS, VK_GROUP, TICKETS_URL,
    VERSION_FILE, BOT_VERSION, OPENAI_API_KEY, GITHUB_REPO
)
from schedulers import setup_schedulers
from auto_updater import AutoUpdater

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Основное меню бота
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎫 Купить билет"),
            KeyboardButton(text="📅 Расписание")
        ],
        [
            KeyboardButton(text="🎭 Косплей-шоу"),
            KeyboardButton(text="💎 Маркет")
        ],
        [
            KeyboardButton(text="❓ FAQ"),
            KeyboardButton(text="📱 Соцсети")
        ],
        [
            KeyboardButton(text="🛟 Поддержка"),
            KeyboardButton(text="🤖 AI-ассистент")
        ]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_command(message: Message):
    welcome_text = f"""🤖 {hbold(f"Добро пожаловать на {EVENT_NAME}!")}

Это был долгий путь, не так ли? 
Присаживайся, ты как раз успел к самому началу, дорогой друг))

➿➿➿➿➿➿➿➿➿➿➿➿

{hbold("НА МЕРОПРИЯТИИ ВАС ОЖИДАЮТ:")}
• 🎁 Подарки к каждому билету!
• 🎭 Конкурсное косплей-дефиле с крутыми призами!
• 💎 Маркет с разнообразным мерчом по лофд от художников!
• 📸 Фото-зоны
• 🌊 Комфортная лаундж-зона с выходом к заливу
• 🎮 Интерактивные стенды с мини-играми и призами!
• 🎵 Концерт и автограф-сессия с группой Восход!
• 🍹 Обновлённый мини-бар с напитками прямо из сезонов!
• 🍱 Вкуснейший японский стрит-фуд

{hbold("Дата:")} {EVENT_DATE}
{hbold("Место:")} {EVENT_LOCATION}
{hbold("Адрес:")} {EVENT_ADDRESS}

➿➿➿➿➿➿➿➿➿➿➿➿

Используйте меню для навигации 👇"""

    await message.answer(welcome_text, reply_markup=main_menu, parse_mode="HTML")

@dp.message()
async def handle_messages(message: Message):
    """Обработчик текстовых сообщений"""
    text = message.text
    menu_commands = {
        "🎫 Купить билет": "tickets",
        "📅 Расписание": "schedule",
        "🎭 Косплей-шоу": "cosplay",
        "💎 Маркет": "market",
        "❓ FAQ": "faq",
        "📱 Соцсети": "social",
        "🛟 Поддержка": "support",
        "🤖 AI-ассистент": "ai_assistant"
    }
    
    if text in menu_commands:
        section = menu_commands[text]
        if section == "ai_assistant":
            await show_ai_assistant_message(message)
        else:
            keyboard = get_section_keyboard(section)
            await message.answer(
                RESPONSE_TEXTS[section],
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

def get_section_keyboard(section: str) -> InlineKeyboardMarkup:
    """Получение клавиатуры для раздела"""
    keyboards = {
        "tickets": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎫 Купить билет", url=TICKETS_URL)],
            [InlineKeyboardButton(text="📜 Правила посещения", url="https://t.me/lolofest2025/41")]
        ]),
        "cosplay": InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Соло", url=REGISTRATION_LINKS['cosplay_solo']),
                InlineKeyboardButton(text="👥 Группа", url=REGISTRATION_LINKS['cosplay_group'])
            ],
            [InlineKeyboardButton(text="📋 Правила", url="https://t.me/lolofest2025/233")]
        ]),
        "market": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Подать заявку", url=REGISTRATION_LINKS['market'])],
            [InlineKeyboardButton(text="ℹ️ Подробнее", url="https://t.me/lolofest2025/236")]
        ]),
        "social": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ВКонтакте", url=VK_GROUP)],
            [InlineKeyboardButton(text="Telegram", url="https://t.me/lolofest2025")]
        ]),
        "support": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Написать организатору", url="https://t.me/cookie_snake")],
            [InlineKeyboardButton(text="📋 Правила чата", url="https://t.me/lolofest2025/rules")]
        ])
    }
    return keyboards.get(section)

async def show_ai_assistant_message(message: Message):
    """Показ сообщения о AI-ассистенте"""
    ai_message = """🤖 *AI-ассистент П.Е.Р.С.И.К.*

💡 *Задайте любой вопрос о фестивале!*

Я могу помочь вам:
• Узнать подробности о мероприятии
• Получить информацию о билетах
• Разобраться с правилами
• Найти нужные контакты
• Ответить на частые вопросы

_{Просто напишите свой вопрос в чат}_"""

    await message.answer(ai_message, parse_mode="Markdown")

async def main():
    # Инициализация автоапдейтера
    updater = AutoUpdater(
        github_repo=GITHUB_REPO,
        current_version=BOT_VERSION,
        version_file=VERSION_FILE
    )
    
    # Проверка обновлений при запуске
    await updater.check_for_updates()
    
    # Настройка и запуск планировщика
    await setup_schedulers()
    
    # Запуск бота
    await dp.start_polling(bot)

def run_bot():
    """Функция запуска бота"""
    # Создание директории для логов
    os.makedirs('logs', exist_ok=True)
    
    # Настройка event loop для Windows
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        bot = BotHandler()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)

if __name__ == '__main__':
    run_bot()
