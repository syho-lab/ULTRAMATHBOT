import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sympy as sp
import re
import logging
import math

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot('ВАШ_TELEGRAM_ТОКЕН')

# Математические символы
x, y, z = sp.symbols('x y z')
pi = sp.pi
e = sp.E
i = sp.I
infty = sp.oo

def clean_expression(text):
    """Очистка и подготовка математического выражения"""
    # Замена всех математических символов
    replacements = {
        # Арифметика
        '^': '**', '×': '*', '÷': '/', '–': '-', '−': '-',
        '\\s+': '', '[,]': '.',
        
        # Сравнение
        '≠': '!=', '≤': '<=', '≥': '>=', '≈': '~',
        '<=': '<=', '>=': '>=',
        
        # Греческие буквы и константы
        'π': 'pi', '∞': 'oo', '℮': 'E',
        'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
        'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
        'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
        'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο', 'pi': 'π',
        'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
        'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
        
        # Множества
        '∈': ' in ', '∉': ' not in ', '⊆': ' subset ', '⊂': ' subset ',
        '⊇': ' superset ', '⊃': ' superset ', '∪': ' union ', '∩': ' intersect ',
        '∖': ' minus ', '∅': 'EmptySet',
        
        # Логика
        '∧': ' and ', '∨': ' or ', '¬': ' not ', '⇒': ' implies ',
        '⇔': ' iff ', '∀': ' forall ', '∃': ' exists ',
        
        # Функции
        '√': 'sqrt', '∫': 'integrate ', '∂': 'diff', '∑': 'Sum',
        '∏': 'Product', '!': 'factorial',
        
        # Другое
        '∇': 'nabla', '⊥': 'perp', '∥': 'parallel', '∠': 'angle',
        '∟': 'rightangle', '°': 'deg', '∆': 'Delta'
    }
    
    for old, new in replacements.items():
        text = re.sub(old, new, text, flags=re.IGNORECASE)
    
    return text.strip()

def solve_expression(expr):
    """Умный решатель с поддержкой всех математических операций"""
    try:
        original_expr = expr
        expr = clean_expression(expr)
        
        # Определяем тип выражения
        if '=' in expr and not any(op in expr for op in ['<=', '>=', '!=']):
            # Уравнение
            left, right = expr.split('=', 1)
            equation = sp.sympify(left) - sp.sympify(right)
            solutions = sp.solve(equation, x)
            
            if solutions:
                result = "🎯 **Решения уравнения:**\n"
                for i, sol in enumerate(solutions, 1):
                    result += f"x{i} = {sp.latex(sol)}\n"
                return result
            else:
                return "❌ Уравнение не имеет решений"
        
        elif 'integrate' in expr.lower() or '∫' in original_expr:
            # Интеграл
            integral_expr = expr.replace('integrate', '').replace('∫', '')
            result = sp.integrate(sp.sympify(integral_expr), x)
            return f"📊 **Интеграл:**\n∫({integral_expr})dx = {sp.latex(result)} + C"
        
        elif 'diff' in expr.lower() or '∂' in original_expr or 'derivative' in expr.lower():
            # Производная
            deriv_expr = expr.replace('diff', '').replace('∂', '').replace('derivative', '')
            result = sp.diff(sp.sympify(deriv_expr), x)
            return f"📈 **Производная:**\nd/dx({deriv_expr}) = {sp.latex(result)}"
        
        elif 'limit' in expr.lower() or 'lim' in expr.lower():
            # Предел
            if '->' in expr:
                lim_expr, point = expr.split('->')
                point = point.strip()
                result = sp.limit(sp.sympify(lim_expr), x, sp.sympify(point))
                return f"📐 **Предел:**\nlim({lim_expr}) = {sp.latex(result)}"
        
        elif 'Sum' in expr or '∑' in original_expr:
            # Сумма ряда
            return solve_series(expr, 'sum')
        
        elif 'Product' in expr or '∏' in original_expr:
            # Произведение
            return solve_series(expr, 'product')
        
        elif 'factorial' in expr or '!' in original_expr:
            # Факториал
            fact_expr = expr.replace('factorial', '').replace('!', '')
            result = sp.factorial(sp.sympify(fact_expr))
            return f"🔢 **Факториал:**\n{fact_expr}! = {result}"
        
        elif any(op in expr for op in ['<=', '>=', '!=', '<', '>']):
            # Неравенство
            return solve_inequality(expr)
        
        else:
            # Простое выражение
            result = sp.sympify(expr)
            simplified = sp.simplify(result)
            
            # Проверяем, является ли результат числом
            if simplified.is_number:
                numeric_result = float(simplified)
                return f"🔢 **Результат:**\n{original_expr} = {simplified}\n\n💡 **Численное значение:** {numeric_result}"
            else:
                return f"🔢 **Результат:**\n{original_expr} = {sp.latex(simplified)}"
            
    except Exception as e:
        logger.error(f"Ошибка решения: {e}")
        return f"❌ Не могу решить это выражение.\n**Ошибка:** {str(e)}\n\n💡 **Проверьте правильность ввода:**\n• Используйте * для умножения\n• Используйте ** для степени\n• Для дробей используйте /"

def solve_series(expr, series_type):
    """Решение сумм и произведений"""
    try:
        if series_type == 'sum':
            result = sp.Sum(sp.sympify(expr.replace('Sum', '')), (x, 1, 10)).doit()
            return f"📊 **Сумма ряда:**\n∑({expr}) = {sp.latex(result)}"
        else:
            result = sp.Product(sp.sympify(expr.replace('Product', '')), (x, 1, 5)).doit()
            return f"📊 **Произведение:**\n∏({expr}) = {sp.latex(result)}"
    except:
        return f"❌ Не могу вычислить {series_type}"

def solve_inequality(expr):
    """Решение неравенств"""
    try:
        if '<=' in expr:
            left, right = expr.split('<=')
            solution = sp.solve_univariate_inequality(
                sp.sympify(left) <= sp.sympify(right), x
            )
        elif '>=' in expr:
            left, right = expr.split('>=')
            solution = sp.solve_univariate_inequality(
                sp.sympify(left) >= sp.sympify(right), x
            )
        elif '<' in expr:
            left, right = expr.split('<')
            solution = sp.solve_univariate_inequality(
                sp.sympify(left) < sp.sympify(right), x
            )
        elif '>' in expr:
            left, right = expr.split('>')
            solution = sp.solve_univariate_inequality(
                sp.sympify(left) > sp.sympify(right), x
            )
        elif '!=' in expr:
            left, right = expr.split('!=')
            solution = sp.solve_univariate_inequality(
                sp.sympify(left) != sp.sympify(right), x
            )
        
        return f"📊 **Решение неравенства:**\n{expr}\n\n**Ответ:** {solution}"
    except:
        return "❌ Не могу решить это неравенство"

def create_main_keyboard():
    """Создает основную клавиатуру"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🧮 Арифметика", callback_data="arithmetic"),
        InlineKeyboardButton("📊 Уравнения", callback_data="equations"),
        InlineKeyboardButton("📈 Производные", callback_data="derivatives"),
        InlineKeyboardButton("📅 Интегралы", callback_data="integrals"),
        InlineKeyboardButton("📐 Пределы", callback_data="limits"),
        InlineKeyboardButton("🔢 Факториалы", callback_data="factorials"),
        InlineKeyboardButton("📚 Суммы/Произведения", callback_data="series"),
        InlineKeyboardButton("🎯 Неравенства", callback_data="inequalities"),
        InlineKeyboardButton("🌟 Сложные задачи", callback_data="complex"),
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
        InlineKeyboardButton("📋 Символы", callback_data="symbols")
    ]
    
    # Добавляем кнопки
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    return keyboard

def create_examples_keyboard(category):
    """Клавиатура с примерами"""
    keyboard = InlineKeyboardMarkup()
    
    examples = {
        "arithmetic": [
            ("2 + 2 × 2", "2+2*2"),
            ("(15 - 3) ÷ 4", "(15-3)/4"),
            ("√16 + 5²", "sqrt(16)+5**2"),
            ("π × 2²", "pi*2**2"),
            ("e² + 1", "E**2+1")
        ],
        "equations": [
            ("x² - 4 = 0", "x**2-4=0"),
            ("2x + 5 = 13", "2*x+5=13"),
            ("x² + 3x - 4 = 0", "x**2+3*x-4=0"),
            ("sin(x) = 0.5", "sin(x)=0.5"),
            ("eˣ = 10", "exp(x)=10")
        ],
        "derivatives": [
            ("d/dx(x³)", "diff x**3"),
            ("d/dx(sin(x))", "diff sin(x)"),
            ("d/dx(ln(x))", "diff ln(x)"),
            ("d/dx(eˣ)", "diff exp(x)"),
            ("∂/∂x(x²y)", "diff x**2*y")
        ],
        "integrals": [
            ("∫x² dx", "integrate x**2"),
            ("∫cos(x) dx", "integrate cos(x)"),
            ("∫eˣ dx", "integrate exp(x)"),
            ("∫sin(x) dx", "integrate sin(x)"),
            ("∫1/x dx", "integrate 1/x")
        ],
        "limits": [
            ("lim(x→0) sin(x)/x", "limit sin(x)/x x->0"),
            ("lim(x→∞) 1/x", "limit 1/x x->oo"),
            ("lim(x→2) (x²-4)/(x-2)", "limit (x**2-4)/(x-2) x->2")
        ],
        "factorials": [
            ("5!", "factorial 5"),
            ("10!", "factorial 10"),
            ("0!", "factorial 0"),
            ("7! ÷ 5!", "factorial(7)/factorial(5)")
        ],
        "series": [
            ("∑(n=1→10) n", "Sum n"),
            ("∑(n=1→5) n²", "Sum n**2"),
            ("∏(n=1→5) n", "Product n"),
            ("∑(k=1→∞) 1/2ᵏ", "Sum 1/2**k")
        ],
        "inequalities": [
            ("x² > 4", "x**2 > 4"),
            ("2x + 1 ≤ 5", "2*x+1 <= 5"),
            ("x² - 3x + 2 ≥ 0", "x**2-3*x+2 >= 0"),
            ("|x - 2| < 3", "abs(x-2) < 3")
        ]
    }
    
    for text, data in examples.get(category, []):
        keyboard.add(InlineKeyboardButton(text, callback_data=f"calc_{data}"))
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return keyboard

def create_symbols_keyboard():
    """Клавиатура с математическими символами"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    symbols = [
        ("π", "pi"), ("e", "E"), ("∞", "oo"), ("√", "sqrt()"),
        ("∫", "integrate "), ("∂", "diff "), ("∑", "Sum "), ("∏", "Product "),
        ("!", "factorial "), ("°", "deg "), ("α", "alpha"), ("β", "beta"),
        ("θ", "theta"), ("λ", "lambda"), ("σ", "sigma"), ("ω", "omega")
    ]
    
    buttons = []
    for symbol, code in symbols:
        buttons.append(InlineKeyboardButton(symbol, callback_data=f"sym_{code}"))
    
    # Добавляем кнопки по 3 в ряд
    for i in range(0, len(buttons), 3):
        row = buttons[i:i+3]
        keyboard.add(*row)
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return keyboard

# Обработчики команд
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
✨ *Добро пожаловать в Math Genius Pro!* ✨

🧠 *Самый мощный математический помощник*
🔢 *Решаю ЛЮБЫЕ примеры мгновенно*
🎯 *Точные решения без ошибок*

*Что я умею:*
✅ Арифметические выражения
✅ Уравнения любой сложности  
✅ Производные и интегралы
✅ Пределы и ряды
✅ Неравенства и факториалы
✅ Матрицы и комплексные числа
✅ И многое другое!

*Поддерживаю ВСЕ математические символы:*
π, ∞, ∫, ∂, ∑, ∏, √, °, α, β, θ, λ, и многие другие!

*Выберите категорию или просто напишите пример:* 🚀
    """
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', 
                     reply_markup=create_main_keyboard())

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 *Math Genius Pro - Полное руководство*

*Как пользоваться:*
Просто напишите пример или используйте кнопки!

*Примеры запросов:*
• `2 + 2 * 2`
• `x^2 - 4 = 0` 
• `diff x**3`
• `integrate sin(x)`
• `limit sin(x)/x x->0`
• `factorial 5`
• `x**2 > 4`

*Поддерживаемые операции:*
➕ Сложение, вычитание, умножение, деление
🔢 Степени (x^2 или x**2), корни (sqrt)
📐 Функции: sin, cos, tan, log, exp, ln
📊 Уравнения, неравенства, системы
📈 Производные, интегралы, пределы
📚 Суммы (∑), произведения (∏), факториалы
🎯 Комплексные числа, матрицы

*Специальные символы:*
π (pi), ∞ (oo), e (E), ∫ (integrate), ∂ (diff)

*Начните прямо сейчас!* 🎉
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['symbols'])
def send_symbols(message):
    symbols_text = """
📋 *Математические символы:*

*Греческие букны:*
α beta, β beta, γ gamma, δ delta, ε epsilon
θ theta, λ lambda, π pi, σ sigma, ω omega

*Операторы:*
√ sqrt - квадратный корень
∫ integrate - интеграл
∂ diff - производная
∑ Sum - сумма ряда
∏ Product - произведение
! factorial - факториал

*Константы:*
π pi ≈ 3.14159
e E ≈ 2.71828
∞ oo - бесконечность

*Использование:* Напишите символ или его название
    """
    bot.send_message(message.chat.id, symbols_text, parse_mode='Markdown',
                   reply_markup=create_symbols_keyboard())

# Обработчик инлайн кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "back":
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="✨ *Выберите категорию:*",
                parse_mode='Markdown',
                reply_markup=create_main_keyboard()
            )
        
        elif call.data == "symbols":
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📋 *Математические символы - выберите:*",
                parse_mode='Markdown',
                reply_markup=create_symbols_keyboard()
            )
        
        elif call.data in ["arithmetic", "equations", "derivatives", "integrals", 
                          "limits", "factorials", "series", "inequalities", "complex"]:
            category_names = {
                "arithmetic": "🧮 Арифметика",
                "equations": "📊 Уравнения", 
                "derivatives": "📈 Производные",
                "integrals": "📅 Интегралы",
                "limits": "📐 Пределы",
                "factorials": "🔢 Факториалы",
                "series": "📚 Суммы и произведения",
                "inequalities": "🎯 Неравенства",
                "complex": "🌟 Сложные задачи"
            }
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id, 
                text=f"*{category_names[call.data]}* - выберите пример:",
                parse_mode='Markdown',
                reply_markup=create_examples_keyboard(call.data)
            )
        
        elif call.data.startswith("calc_"):
            expression = call.data[5:]  # Убираем "calc_"
            solution = solve_expression(expression)
            
            response_text = f"""
*Пример:* `{expression}`

*Решение:*
{solution}

*Решено мгновенно!* ⚡
*Хотите решить ещё?* 🎯
            """
            
            bot.send_message(call.message.chat.id, response_text, 
                           parse_mode='Markdown')
        
        elif call.data.startswith("sym_"):
            symbol = call.data[4:]  # Убираем "sym_"
            bot.answer_callback_query(call.id, f"Символ {symbol} - используйте в выражениях")
        
        elif call.data == "help":
            send_help(call.message)
            
    except Exception as e:
        logger.error(f"Ошибка в callback: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")

# Обработчик текстовых сообщений  
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_input = message.text
        
        if len(user_input) > 200:
            bot.reply_to(message, "❌ Слишком длинное выражение. Максимум 200 символов.")
            return
        
        # Показываем "печатает"
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Решаем пример
        solution = solve_expression(user_input)
        
        # Отправляем результат
        response_text = f"""
🎯 *Ваш пример:* `{user_input}`

📚 *Решение:*
{solution}

⚡ *Решено с математической точностью!*
🔢 *Новый пример?* Просто напишите!
        """
        
        bot.reply_to(message, response_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при решении. Проверьте правильность ввода.\n\n💡 *Используйте /help для справки*", parse_mode='Markdown')

if __name__ == "__main__":
    logger.info("Math Genius Pro запущен!")
    bot.polling(none_stop=True)
