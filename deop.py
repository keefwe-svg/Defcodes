import telebot
from telebot import types
import os
import json
import logging
from datetime import datetime
import random
import string

# ========== КОНФИГУРАЦИЯ ==========
TOKEN = "8618294513:AAEikwKHFgVTrb04sAyIY-wcG0yekAkrHo"
bot = telebot.TeleBot(TOKEN)

ADMIN_IDS = [6333503076, 8037857188]  # ID админов

# Файлы для хранения данных
USERS_FILE = "users_data.json"
ORDERS_FILE = "orders_data.json"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Состояния для заказов
ORDER_STATES = {}

# Категории заказов
CATEGORIES = {
    "website": "🌐 Сайт",
    "telegram_bot": "🤖 Бот Telegram",
    "minecraft_plugin": "🧩 Плагин Minecraft",
    "other": "❌ Прочее"
}

# ========== РАБОТА С ДАННЫМИ ==========

def load_users_data():
    """Загружает данные пользователей"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
    return {}

def save_users_data(users_data):
    """Сохраняет данные пользователей"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

def load_orders_data():
    """Загружает данные заказов"""
    try:
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки заказов: {e}")
    return {}

def save_orders_data(orders_data):
    """Сохраняет данные заказов"""
    try:
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения заказов: {e}")

def get_user_data(user_id):
    """Получает данные пользователя"""
    users_data = load_users_data()
    user_id_str = str(user_id)
    
    if user_id_str not in users_data:
        users_data[user_id_str] = {
            "username": "",
            "stars_balance": 0,
            "total_spent_stars": 0,
            "purchases_count": 0,
            "orders": [],
            "registration_date": datetime.now().isoformat()
        }
        save_users_data(users_data)
    
    return users_data[user_id_str]

def update_user_data(user_id, data_update):
    """Обновляет данные пользователя"""
    users_data = load_users_data()
    user_id_str = str(user_id)
    
    if user_id_str not in users_data:
        users_data[user_id_str] = {}
    
    users_data[user_id_str].update(data_update)
    save_users_data(users_data)

def add_transaction(user_id, amount, transaction_type="stars_purchase", description=""):
    """Добавляет транзакцию и обновляет баланс"""
    user_data = get_user_data(user_id)
    
    transaction = {
        "date": datetime.now().isoformat(),
        "amount": amount,
        "type": transaction_type,
        "description": description,
        "balance_after": user_data.get("stars_balance", 0) + amount
    }
    
    if "transactions" not in user_data:
        user_data["transactions"] = []
    
    user_data["transactions"].append(transaction)
    
    # Обновляем баланс
    new_balance = user_data.get("stars_balance", 0) + amount
    user_data["stars_balance"] = new_balance
    
    if amount > 0:
        user_data["total_spent_stars"] = user_data.get("total_spent_stars", 0) + amount
        user_data["purchases_count"] = user_data.get("purchases_count", 0) + 1
    
    update_user_data(user_id, user_data)
    return new_balance

# ========== КЛАВИАТУРЫ ==========

def main_menu(user_id=None):
    """Главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('👤 Профиль')
    btn2 = types.KeyboardButton('📦 Заказать')
    btn3 = types.KeyboardButton('⭐ Пополнить Stars')
    btn4 = types.KeyboardButton('📊 Мои заказы')
    btn5 = types.KeyboardButton('🆘 Помощь')
    
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

def categories_menu():
    """Меню выбора категории заказа"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for key, name in CATEGORIES.items():
        markup.add(types.KeyboardButton(name))
    
    markup.add(types.KeyboardButton('🔙 Назад'))
    return markup

def profile_menu():
    """Меню профиля"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('⭐ Пополнить Stars')
    btn2 = types.KeyboardButton('📊 Мои заказы')
    btn3 = types.KeyboardButton('🔙 Назад')
    markup.add(btn1, btn2, btn3)
    return markup

def payment_amount_menu():
    """Меню пополнения"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    amounts = ['10 ⭐', '25 ⭐', '50 ⭐', '100 ⭐', '200 ⭐', '500 ⭐']
    for amount in amounts:
        markup.add(types.KeyboardButton(amount))
    markup.add(types.KeyboardButton('🔙 Назад'))
    return markup

# ========== ОСНОВНЫЕ КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    user = message.from_user
    user_data = {
        "username": user.username or user.first_name,
        "last_active": datetime.now().isoformat()
    }
    update_user_data(user.id, user_data)
    
    welcome_text = """
🤖 **Добро пожаловать в бот заказов!**

Здесь вы можете заказать:
• 🌐 Сайт
• 🤖 Бота Telegram
• 🧩 Плагин для Minecraft

💰 Оплата производится в **Telegram Stars** ⭐

Используйте кнопки ниже для навигации:
    """
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(user.id))

@bot.message_handler(commands=['profile'])
def profile_command(message):
    """Обработчик команды /profile"""
    show_profile(message)

@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def show_profile(message):
    """Показать профиль пользователя"""
    user = message.from_user
    user_data = get_user_data(user.id)
    
    username = user_data.get('username', user.username or user.first_name)
    stars_balance = user_data.get('stars_balance', 0)
    total_spent = user_data.get('total_spent_stars', 0)
    purchases_count = user_data.get('purchases_count', 0)
    orders_count = len(user_data.get('orders', []))
    
    profile_text = f"""
👤 **Ваш профиль**

📛 Имя: @{username}
🆔 ID: {user.id}
⭐ Баланс Stars: {stars_balance}
📈 Всего потрачено: {total_spent} ⭐
🛍️ Количество покупок: {purchases_count}
📦 Всего заказов: {orders_count}

📅 Дата регистрации: {user_data.get('registration_date', 'Неизвестно')[:10]}
    """
    bot.send_message(message.chat.id, profile_text, reply_markup=profile_menu())

@bot.message_handler(func=lambda message: message.text == '📦 Заказать')
def start_order(message):
    """Начать оформление заказа"""
    user_id = message.from_user.id
    
    ORDER_STATES[user_id] = {
        "step": "category",
        "data": {}
    }
    
    bot.send_message(
        message.chat.id,
        "📦 **Оформление заказа**\n\nВыберите категорию:",
        reply_markup=categories_menu()
    )

@bot.message_handler(func=lambda message: message.text in CATEGORIES.values())
def handle_category(message):
    """Обработка выбора категории"""
    user_id = message.from_user.id
    
    if user_id not in ORDER_STATES:
        start_order(message)
        return
    
    # Находим ключ категории
    category_key = None
    for key, name in CATEGORIES.items():
        if name == message.text:
            category_key = key
            break
    
    if category_key == "other":
        bot.send_message(message.chat.id, "❌ Категория 'Прочее' временно недоступна.")
        ORDER_STATES.pop(user_id, None)
        bot.send_message(message.chat.id, "Возврат в главное меню", reply_markup=main_menu(user_id))
        return
    
    ORDER_STATES[user_id]["data"]["category"] = category_key
    ORDER_STATES[user_id]["step"] = "name"
    
    bot.send_message(message.chat.id, "📝 Введите **название** вашего заказа:")

@bot.message_handler(func=lambda message: message.from_user.id in ORDER_STATES and 
                     ORDER_STATES[message.from_user.id].get("step") == "name")
def handle_order_name(message):
    """Обработка названия заказа"""
    user_id = message.from_user.id
    ORDER_STATES[user_id]["data"]["name"] = message.text
    ORDER_STATES[user_id]["step"] = "description"
    
    bot.send_message(message.chat.id, "📄 Введите **описание** заказа:")

@bot.message_handler(func=lambda message: message.from_user.id in ORDER_STATES and 
                     ORDER_STATES[message.from_user.id].get("step") == "description")
def handle_order_description(message):
    """Обработка описания заказа"""
    user_id = message.from_user.id
    ORDER_STATES[user_id]["data"]["description"] = message.text
    ORDER_STATES[user_id]["step"] = "price_stars"
    
    bot.send_message(message.chat.id, "💰 Введите желаемую **цену в Stars** (только число):")

@bot.message_handler(func=lambda message: message.from_user.id in ORDER_STATES and 
                     ORDER_STATES[message.from_user.id].get("step") == "price_stars")
def handle_order_price_stars(message):
    """Обработка цены в Stars"""
    user_id = message.from_user.id
    
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
        ORDER_STATES[user_id]["data"]["price_stars"] = price
        ORDER_STATES[user_id]["step"] = "price_usdt"
        
        bot.send_message(message.chat.id, "💰 Введите желаемую **цену в USDT** (можно дробное):")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите целое положительное число Stars:")

@bot.message_handler(func=lambda message: message.from_user.id in ORDER_STATES and 
                     ORDER_STATES[message.from_user.id].get("step") == "price_usdt")
def handle_order_price_usdt(message):
    """Обработка цены в USDT"""
    user_id = message.from_user.id
    
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError
        
        ORDER_STATES[user_id]["data"]["price_usdt"] = price
        ORDER_STATES[user_id]["data"]["user_id"] = user_id
        ORDER_STATES[user_id]["data"]["username"] = message.from_user.username or message.from_user.first_name
        ORDER_STATES[user_id]["data"]["status"] = "pending"
        ORDER_STATES[user_id]["data"]["created_at"] = datetime.now().isoformat()
        
        # Сохраняем заказ
        order_data = ORDER_STATES[user_id]["data"]
        
        orders = load_orders_data()
        order_id = f"ORD_{int(datetime.now().timestamp())}_{user_id}"
        order_data["order_id"] = order_id
        orders[order_id] = order_data
        save_orders_data(orders)
        
        # Отправляем уведомление админам
        notify_admins(order_data)
        
        bot.send_message(
            message.chat.id,
            f"✅ **Заказ #{order_id[:15]} отправлен!**\n\n"
            f"Администраторы рассмотрят вашу заявку в ближайшее время.\n"
            f"Вы получите уведомление о решении.",
            reply_markup=main_menu(user_id)
        )
        
        # Очищаем состояние
        ORDER_STATES.pop(user_id, None)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите положительное число USDT:")

def notify_admins(order_data):
    """Отправляет уведомление админам о новом заказе"""
    category_name = CATEGORIES.get(order_data["category"], order_data["category"])
    
    text = f"""
🆕 **НОВЫЙ ЗАКАЗ!** 🆕

📋 **Информация:**
🆔 Заказ: `{order_data['order_id']}`
👤 От: @{order_data['username']} (ID: {order_data['user_id']})
📂 Категория: {category_name}
📝 Название: {order_data['name']}
📄 Описание: {order_data['description']}
💰 Цена: {order_data['price_stars']} ⭐ / {order_data['price_usdt']} USDT

Используйте кнопки ниже для ответа:
    """
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_accept = types.InlineKeyboardButton(
        "✅ Принять", 
        callback_data=f"accept_{order_data['order_id']}"
    )
    btn_reject = types.InlineKeyboardButton(
        "❌ Отказать", 
        callback_data=f"reject_{order_data['order_id']}"
    )
    markup.add(btn_accept, btn_reject)
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Не удалось отправить админу {admin_id}: {e}")

# ========== ОБРАБОТКА РЕШЕНИЙ АДМИНОВ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_') or call.data.startswith('reject_'))
def handle_admin_decision(call):
    """Обработка решения админа (принять/отказать)"""
    action, order_id = call.data.split('_', 1)
    
    orders = load_orders_data()
    order = orders.get(order_id)
    
    if not order:
        bot.answer_callback_query(call.id, "Заказ не найден!")
        return
    
    if action == 'accept':
        # Сохраняем в состояние админа для ввода цены
        bot.answer_callback_query(call.id, "Введите цену в Stars для этого заказа")
        
        # Просим админа ввести цену
        msg = bot.send_message(
            call.message.chat.id,
            f"💰 Введите **финальную цену в Stars** для заказа:\n"
            f"📝 Заказ: {order['name']}\n"
            f"👤 Пользователь: @{order['username']}\n"
            f"📊 Предложенная цена: {order['price_stars']} ⭐\n\n"
            f"Введите число или 'cancel' для отмены:"
        )
        
        # Сохраняем контекст для следующего шага
        bot.register_next_step_handler(msg, process_accept_price, order_id, call.message.chat.id)
        
    elif action == 'reject':
        # Отклоняем заказ
        order["status"] = "rejected"
        order["rejected_at"] = datetime.now().isoformat()
        order["rejected_by"] = call.from_user.username or call.from_user.first_name
        save_orders_data(orders)
        
        # Уведомляем пользователя
        try:
            bot.send_message(
                order["user_id"],
                f"❌ **Ваш заказ был отклонен администратором!**\n\n"
                f"📝 Заказ: {order['name']}\n"
                f"Причина: Администратор отклонил заявку.\n\n"
                f"Вы можете создать новый заказ через кнопку '📦 Заказать'"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить пользователя {order['user_id']}: {e}")
        
        bot.edit_message_text(
            f"❌ Заказ #{order_id} отклонен\n\n"
            f"Пользователь: @{order['username']}\n"
            f"Название: {order['name']}",
            call.message.chat.id,
            call.message.message_id
        )
        
        bot.answer_callback_query(call.id, "Заказ отклонен")

def process_accept_price(message, order_id, admin_chat_id):
    """Обработка ввода цены админом"""
    if message.text.lower() == 'cancel':
        bot.send_message(message.chat.id, "❌ Отмена принятия заказа.")
        return
    
    try:
        final_price = int(message.text)
        if final_price <= 0:
            raise ValueError
        
        orders = load_orders_data()
        order = orders.get(order_id)
        
        if not order:
            bot.send_message(message.chat.id, "❌ Заказ не найден!")
            return
        
        # Обновляем заказ
        order["status"] = "accepted"
        order["final_price_stars"] = final_price
        order["accepted_at"] = datetime.now().isoformat()
        order["accepted_by"] = message.from_user.username or message.from_user.first_name
        save_orders_data(orders)
        
        # Отправляем счет пользователю
        send_payment_invoice(order["user_id"], order, final_price)
        
        bot.send_message(
            message.chat.id,
            f"✅ Заказ #{order_id[:15]} принят!\n"
            f"💰 Финальная цена: {final_price} ⭐\n"
            f"Счет отправлен пользователю."
        )
        
        # Обновляем сообщение админа
        bot.send_message(
            admin_chat_id,
            f"✅ Заказ #{order_id} принят с ценой {final_price} ⭐\n"
            f"Пользователь: @{order['username']}"
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите целое положительное число Stars!")
        # Повторно запрашиваем цену
        msg = bot.send_message(
            message.chat.id,
            f"💰 Введите **финальную цену в Stars** (целое число):"
        )
        bot.register_next_step_handler(msg, process_accept_price, order_id, admin_chat_id)

def send_payment_invoice(user_id, order, price_stars):
    """Отправляет счет на оплату Stars"""
    title = f"Заказ: {order['name'][:50]}"
    description = f"Категория: {CATEGORIES.get(order['category'], order['category'])}\nОписание: {order['description'][:200]}"
    payload = f"order_{order['order_id']}_{user_id}"
    
    prices = [types.LabeledPrice(label="Оплата заказа", amount=price_stars)]
    
    try:
        bot.send_invoice(
            chat_id=user_id,
            title=title,
            description=description,
            invoice_payload=payload,
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter=f"order_{order['order_id']}",
            photo_url="https://img.icons8.com/color/96/000000/shopping-cart--v1.png",
            photo_width=96,
            photo_height=96,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        logger.info(f"Счет на {price_stars} Stars отправлен пользователю {user_id} для заказа {order['order_id']}")
    except Exception as e:
        logger.error(f"Ошибка отправки счета: {e}")
        bot.send_message(
            user_id,
            f"❌ Ошибка при создании счета. Пожалуйста, обратитесь в поддержку.\nОшибка: {str(e)[:100]}"
        )

# ========== ПЛАТЕЖИ ==========

@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query(pre_checkout_q):
    """Обработка предварительной проверки платежа"""
    try:
        if pre_checkout_q.invoice_payload.startswith('order_'):
            bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
            logger.info(f"Pre-checkout подтвержден: {pre_checkout_q.invoice_payload}")
        elif pre_checkout_q.invoice_payload.startswith('stars_'):
            bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
        else:
            bot.answer_pre_checkout_query(pre_checkout_q.id, ok=False, 
                                         error_message="Неверный идентификатор платежа")
    except Exception as e:
        logger.error(f"Ошибка pre-checkout: {e}")
        bot.answer_pre_checkout_query(pre_checkout_q.id, ok=False, 
                                     error_message="Ошибка обработки платежа")

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    """Обработка успешного платежа"""
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    logger.info(f"Успешный платеж: {payload}, сумма: {payment.total_amount} {payment.currency}")
    
    if payload.startswith('order_'):
        # Платеж за заказ
        parts = payload.split('_')
        if len(parts) >= 3:
            order_id = parts[1]
            user_id = int(parts[2])
            
            orders = load_orders_data()
            order = orders.get(order_id)
            
            if order and order.get("status") == "accepted":
                order["status"] = "paid"
                order["paid_at"] = datetime.now().isoformat()
                order["paid_amount"] = payment.total_amount
                save_orders_data(orders)
                
                # Обновляем профиль пользователя
                add_transaction(user_id, -payment.total_amount, "order_payment", f"Оплата заказа: {order['name']}")
                
                # Уведомляем пользователя
                success_text = f"""
🎉 **Оплата успешна!** 🎉

✅ Заказ **{order['name']}** оплачен!
💰 Сумма: {payment.total_amount} ⭐

Администратор свяжется с вами для выполнения заказа.
Спасибо за доверие!
                """
                bot.send_message(message.chat.id, success_text, reply_markup=main_menu(user_id))
                
                # Уведомляем админов
                for admin_id in ADMIN_IDS:
                    bot.send_message(
                        admin_id,
                        f"💰 **ЗАКАЗ ОПЛАЧЕН!**\n\n"
                        f"🆔 Заказ: {order_id}\n"
                        f"👤 Пользователь: @{order['username']}\n"
                        f"📝 Название: {order['name']}\n"
                        f"💰 Сумма: {payment.total_amount} ⭐\n\n"
                        f"Свяжитесь с пользователем для выполнения заказа."
                    )
                
                logger.info(f"Заказ {order_id} оплачен пользователем {user_id}")
    
    elif payload.startswith('stars_'):
        # Пополнение баланса Stars
        parts = payload.split('_')
        if len(parts) >= 3:
            amount = int(parts[1])
            user_id = int(parts[2])
            
            new_balance = add_transaction(user_id, amount, "stars_purchase", f"Пополнение на {amount} Stars")
            
            success_text = f"""
🎉 **Пополнение успешно!** 🎉

✅ Ваш баланс пополнен на {amount} ⭐
💰 Новый баланс: {new_balance} ⭐

Теперь вы можете использовать Stars для заказов!
            """
            bot.send_message(message.chat.id, success_text, reply_markup=main_menu(user_id))

# ========== ПОПОЛНЕНИЕ БАЛАНСА ==========

@bot.message_handler(func=lambda message: message.text == '⭐ Пополнить Stars')
def add_balance(message):
    """Показать меню пополнения баланса"""
    text = """
⭐ **Пополнение STARS**

Выберите количество Stars для пополнения:

💡 Stars используются для оплаты заказов
    """
    bot.send_message(message.chat.id, text, reply_markup=payment_amount_menu())

@bot.message_handler(func=lambda message: message.text.endswith('⭐') and message.text[:-2].strip().isdigit())
def handle_payment_amount(message):
    """Обработка выбора суммы для пополнения"""
    amount = int(message.text.split()[0])
    user_id = message.from_user.id
    
    prices = [types.LabeledPrice(label="Пополнение Stars", amount=amount)]
    
    try:
        bot.send_invoice(
            chat_id=message.chat.id,
            title=f"Пополнение STARS на {amount}",
            description=f"Покупка {amount} Stars для использования в боте",
            invoice_payload=f"stars_{amount}_{user_id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter=f"stars_{amount}",
            photo_url="https://img.icons8.com/color/96/000000/star--v1.png",
            photo_width=96,
            photo_height=96,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        logger.info(f"Создан счет на {amount} Stars для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка создания счета: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)[:200]}")

# ========== МОИ ЗАКАЗЫ ==========

@bot.message_handler(func=lambda message: message.text == '📊 Мои заказы')
def show_my_orders(message):
    """Показать историю заказов пользователя"""
    user_id = message.from_user.id
    orders = load_orders_data()
    
    user_orders = [o for o in orders.values() if o.get("user_id") == user_id]
    
    if not user_orders:
        bot.send_message(message.chat.id, "📭 У вас пока нет заказов.\n\nНажмите '📦 Заказать' чтобы создать новый заказ.")
        return
    
    status_emoji = {
        "pending": "⏳",
        "accepted": "✅",
        "rejected": "❌",
        "paid": "💰"
    }
    
    status_text = {
        "pending": "Ожидает рассмотрения",
        "accepted": "Принят (ожидает оплаты)",
        "rejected": "Отклонен",
        "paid": "Оплачен (в работе)"
    }
    
    text = f"📊 **Ваши заказы (всего: {len(user_orders)})**\n\n"
    
    for order in user_orders[-10:]:  # Показываем последние 10
        status = order.get("status", "pending")
        emoji = status_emoji.get(status, "❓")
        text += f"{emoji} **{order.get('name', 'Без названия')[:30]}**\n"
        text += f"   🆔 ID: {order.get('order_id', 'N/A')[:15]}...\n"
        text += f"   📂 {CATEGORIES.get(order.get('category', ''), order.get('category', 'Неизвестно'))}\n"
        text += f"   📊 Статус: {status_text.get(status, status)}\n"
        
        if order.get("final_price_stars"):
            text += f"   💰 Цена: {order.get('final_price_stars')} ⭐\n"
        elif order.get("price_stars"):
            text += f"   💰 Предложено: {order.get('price_stars')} ⭐\n"
        
        created_at = order.get("created_at", "")
        if created_at:
            text += f"   📅 Создан: {created_at[:10]}\n"
        text += "\n"
    
    bot.send_message(message.chat.id, text)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def back_to_main(message):
    """Возврат в главное меню"""
    user_id = message.from_user.id
    ORDER_STATES.pop(user_id, None)
    bot.send_message(message.chat.id, "🔙 Возврат в главное меню", reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text == '🆘 Помощь')
def help_command(message):
    """Помощь"""
    help_text = """
🆘 **Помощь**

📋 **Как сделать заказ:**
1. Нажмите кнопку "📦 Заказать"
2. Выберите категорию
3. Введите название и описание
4. Укажите желаемую цену
5. Ожидайте решения администратора

💰 **Оплата:**
• Все заказы оплачиваются в Telegram Stars ⭐
• Пополнить баланс можно через кнопку "⭐ Пополнить Stars"

📞 **Поддержка:**
При возникновении вопросов обращайтесь к администраторам.
    """
    bot.send_message(message.chat.id, help_text, reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработка всех остальных сообщений"""
    # Игнорируем сообщения во время оформления заказа
    if message.from_user.id in ORDER_STATES:
        return
    
    bot.send_message(message.chat.id, "🤖 Используйте кнопки для навигации!", 
                    reply_markup=main_menu(message.from_user.id))

# ========== ЗАПУСК БОТА ==========

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Бот запускается...")
    print("=" * 50)
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"📁 Файлы данных: {USERS_FILE}, {ORDERS_FILE}")
    print("=" * 50)
    print("✅ Бот готов к работе!")
    print("=" * 50)
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")