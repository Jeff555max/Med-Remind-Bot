import telebot
import random
import datetime
import time
import threading

API_TOKEN = '7945599886:AAEgoIJEkhgoy-ltY5bYbGaGlb3oiEx9uA8'
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения времени напоминаний каждого пользователя
user_reminder_times = {}  # {user_id: {'morning': time, 'afternoon': time, 'evening': time}}

# Список интересных фактов о витаминах
vitamin_facts = [
    "Витамин C способствует укреплению иммунной системы.",
    "Витамин D помогает усваивать кальций и укрепляет кости.",
    "Витамин A важен для здоровья зрения и кожи.",
    "Витамин E является антиоксидантом и защищает клетки от повреждений.",
    "Витамин K необходим для свертывания крови и здоровья костей.",
    "Витамины группы B важны для обмена веществ и нервной системы.",
    "Витамин B12 помогает в образовании красных кровяных клеток и поддерживает нервную систему.",
    "Витамин B6 участвует в синтезе нейротрансмиттеров и метаболизме аминокислот.",
    "Фолиевая кислота (витамин B9) важна для роста и развития клеток.",
    "Биотин (витамин B7) способствует здоровью кожи, волос и ногтей.",
    # Добавьте больше фактов при необходимости
]

# Функция для отображения всех доступных команд
def show_commands(message):
    commands = (
        "/set_times - Установить время напоминаний\n"
        "/fact - Получить случайный факт о витаминах\n"
        "/help - Показать список команд"
    )
    bot.reply_to(message, "Выберите команду:\n" + commands)

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот, который поможет вам не забыть принимать ваши лекарства и витамины три раза в день.\n"
        "Вы можете установить время напоминаний с помощью команды /set_times.\n"
        "Также вы можете получить случайный факт о витаминах, отправив команду /fact.\n"
        "Для получения дополнительной информации используйте команду /help."
    )
    show_commands(message)  # Показываем список команд сразу после приветственного сообщения

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        "Я напомню вам принять лекарства и витамины утром, днем и вечером.\n"
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/set_times - Установить время напоминаний\n"
        "/fact - Получить случайный факт о витаминах"
    )
    show_commands(message)

# Команда /set_times для установки времени напоминаний
@bot.message_handler(commands=['set_times'])
def set_times(message):
    msg = bot.reply_to(message, "Пожалуйста, введите время для утреннего напоминания в формате ЧЧ:ММ (например, 08:00):")
    bot.register_next_step_handler(msg, process_morning_time_step)

def process_morning_time_step(message):
    try:
        morning_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        user_id = message.chat.id
        if user_id not in user_reminder_times:
            user_reminder_times[user_id] = {}
        user_reminder_times[user_id]['morning'] = morning_time
        msg = bot.reply_to(message, "Теперь введите время для дневного напоминания в формате ЧЧ:ММ (например, 13:00):")
        bot.register_next_step_handler(msg, process_afternoon_time_step)
    except ValueError:
        msg = bot.reply_to(message, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ.")
        bot.register_next_step_handler(msg, process_morning_time_step)

def process_afternoon_time_step(message):
    try:
        afternoon_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        user_id = message.chat.id
        user_reminder_times[user_id]['afternoon'] = afternoon_time
        msg = bot.reply_to(message, "Теперь введите время для вечернего напоминания в формате ЧЧ:ММ (например, 20:00):")
        bot.register_next_step_handler(msg, process_evening_time_step)
    except ValueError:
        msg = bot.reply_to(message, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ.")
        bot.register_next_step_handler(msg, process_afternoon_time_step)

def process_evening_time_step(message):
    try:
        evening_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        user_id = message.chat.id
        user_reminder_times[user_id]['evening'] = evening_time
        bot.reply_to(message, "Время напоминаний установлено!")
        show_commands(message)
    except ValueError:
        msg = bot.reply_to(message, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ.")
        bot.register_next_step_handler(msg, process_evening_time_step)

# Команда /fact для отправки случайного факта
@bot.message_handler(commands=['fact'])
def send_fact(message):
    fact = random.choice(vitamin_facts)
    bot.reply_to(message, fact)
    show_commands(message)

# Функция напоминания
def reminder():
    while True:
        now = datetime.datetime.now()
        current_time = now.time()
        for user_id, times in user_reminder_times.items():
            for period, reminder_time in times.items():
                # Проверяем, совпадает ли текущее время с временем напоминания
                if (current_time.hour == reminder_time.hour and
                    current_time.minute == reminder_time.minute and
                    now.second == 0):
                    try:
                        bot.send_message(user_id, f"Напоминание: Пора принять ваши лекарства и витамины ({period})!")
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        time.sleep(1)

# Запуск функции напоминания в отдельном потоке
reminder_thread = threading.Thread(target=reminder)
reminder_thread.daemon = True
reminder_thread.start()

# Запуск бота
bot.polling()