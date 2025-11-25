import os
import telebot
import sympy as sp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверяем токен
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не найден в переменных окружения!")
    logger.error("Добавьте TELEGRAM_TOKEN в Environment Variables в Render")
    exit(1)

logger.info(f"✅ Токен получен, запускаем бота...")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Простой решатель
def solve_math(expression):
    try:
        # Заменяем символы для SymPy
        expr = expression.replace('^', '**').replace('×', '*').replace('÷', '/')
        
        if '=' in expr:
            # Уравнение
            left, right = expr.split('=')
            x = sp.Symbol('x')
            equation = sp.sympify(left) - sp.sympify(right)
            solutions = sp.solve(equation, x)
            return f"Решения: {solutions}"
        else:
            # Простое выражение
            result = sp.sympify(expr)
            return f"Результат: {result}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🤖 *Math Genius Bot*

Привет! Я решаю математические примеры.

*Примеры:*
• 2+2*2
• x^2-4=0
• (15-3)/4

Просто напиши пример! 🚀
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🧮 Примеры", callback_data="examples"))
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown',
                     reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_input = message.text
        
        if len(user_input) > 100:
            bot.reply_to(message, "❌ Слишком длинное выражение")
            return
            
        bot.send_chat_action(message.chat.id, 'typing')
        solution = solve_math(user_input)
        
        response = f"""
🎯 *Пример:* `{user_input}`
📚 *Решение:* {solution}
        """
        
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "examples":
        examples_text = """
📋 *Примеры для теста:*
`2+2*2`
`x^2-4=0` 
`(15-3)/4`
`sqrt(16)`
`pi*2`
        """
        bot.send_message(call.message.chat.id, examples_text, parse_mode='Markdown')

if __name__ == "__main__":
    logger.info("🚀 Запускаем Math Genius Bot...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
