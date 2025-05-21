import telebot
from telebot import types
import sqlite3
import datetime
Bot_Token = '7504411607:AAF94hIkBCH_zzbWGD-ePQP2OTzZCDx6UQI'
bot = telebot.TeleBot(Bot_Token)
users = {}
booking ={}
def init_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS room_types (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        amenities TEXT,
        available_count INTEGER DEFAULT 0
    )
    ''')

    # Создание таблицы бронирований
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        FOREIGN KEY(room_type) REFERENCES room_types(name)
    )
    ''')

    # Проверяем, есть ли уже типы номеров в базе
    cursor.execute("SELECT COUNT(*) FROM room_types")
    if cursor.fetchone()[0] == 0:
        # Добавляем типы номеров с описанием и ценами
        room_types = [
            ('Стандарт',
             'Уютный номер площадью 20-25 м² с одной двуспальной или двумя односпальными кроватями',
             3500.00,
             'Wi-Fi, Телевизор, Кондиционер, Фен, Мини-бар, Сейф',
             10),  # 10 доступных номеров

            ('Люкс',
             'Просторный номер площадью 35-40 м² с отдельной гостиной зоной',
             7500.00,
             'Wi-Fi, Телевизор, Кофемашина, Мини-бар, Халаты, Джакузи',
             5),  # 5 доступных номеров

            ('VIP',
             'Эксклюзивный номер площадью 50-60 м² с панорамным видом',
             12000.00,
             'Wi-Fi, Телевизор, Премиум мини-бар, Гидромассаж, Консьерж-сервис',
             3)  # 3 доступных номера
        ]
        cursor.executemany(
            "INSERT INTO room_types (name, description, price, amenities, available_count) VALUES (?, ?, ?, ?, ?)",
            room_types)

    conn.commit()
    conn.close()


init_db()


# Функция для проверки доступности номеров
def check_availability(room_type, start_date, end_date):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    # Получаем общее количество номеров этого типа
    cursor.execute("SELECT available_count FROM room_types WHERE name = ?", (room_type,))
    total_rooms = cursor.fetchone()[0]

    # Получаем количество занятых номеров на эти даты
    cursor.execute('''
    SELECT COUNT(*) FROM bookings 
    WHERE room_type = ? AND status = 'active'
    AND ((start_date <= ? AND end_date >= ?)
    OR (start_date <= ? AND end_date >= ?))
    ''', (room_type, end_date, start_date, start_date, end_date))

    booked_rooms = cursor.fetchone()[0]
    conn.close()

    return total_rooms - booked_rooms > 0


# Функция для создания бронирования
def create_booking(user_id, room_type, start_date, end_date):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO bookings (user_id, room_type, start_date, end_date)
    VALUES (?, ?, ?, ?)
    ''', (user_id, room_type, start_date, end_date))

    conn.commit()
    conn.close()
def glavnoe_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    guest_button = types.KeyboardButton("Забронировать номер")
    cancel_button = types.KeyboardButton("Отменить бронь")
    markup.add(guest_button, cancel_button)
    return markup
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = glavnoe_menu()
    bot.send_message(chat_id, "Добро пожаловать, здесь можно сделать бронирование номера!", reply_markup=markup)
    users[chat_id] = 'guest'
@bot.message_handler(func=lambda message: message.text in ['Забронировать номер','Отменить бронь'] and users.get(message.chat.id) == 'guest')
def menu_booking(message):
    chat_id = message.chat.id
    if message.text.strip() == 'Забронировать номер':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        vip_button = types.KeyboardButton("VIP")
        lux_button = types.KeyboardButton("Люкс")
        standart_button = types.KeyboardButton("Стандарт")
        markup.add(vip_button, lux_button, standart_button)
        bot.send_message(chat_id, "Пожалуйста, выберете какой номер вы хотите",reply_markup = markup)
    elif message.text.strip() == 'Отменить бронь':
        bot.send_message(chat_id, 'Бронь отменена', reply_markup = glavnoe_menu())
@bot.message_handler(func=lambda message: message.text in ['VIP','Люкс', 'Стандарт'])
def choiced_room(message):
    chat_id = message.chat.id
    room = message.text.strip()
    users[chat_id]['room']=room
    if room == 'VIP':
        bot.send_message(chat_id, 'Вы выбрали VIP-номер ')
    elif room == "Люкс":
        bot.send_message(chat_id, 'Вы выбрали Люкс-номер')
    elif room == 'Стандарт':
        bot.send_message(chat_id, 'Вы выбрали Стандарт - номер')
    bot.send_message(chat_id, 'Укажите дату заезда и дату отъезда в формате-День.Месяц.Год')
    bot.register_next_step_handler(message,book_data)
def book_data(message):
    chat_id= message.chat.id
    try:
        first_datazaezd, last_dataotezd = message.text.split('-')
        first_datazaezd = datetime.datetime.strptime(first_datazaezd.strip(), "%d.%m.%Y").date()
        last_dataotezd = datetime.datetime.strptime(last_dataotezd.strip(), "%d.%m.%Y").date()
        if last_dataotezd<=first_datazaezd:
            bot.send_message(chat_id, 'Неверно введена дата, пожалуйста проверьте корректность даты')
            bot.register_next_step_handler(message, book_data)
            return
        else:
             users[chat_id]['first_datazaezd'] = first_datazaezd
             users[chat_id]['last_dataotezd'] = last_dataotezd
             potver_book(message)
    except ValueError:
        bot.send_message(chat_id, "Произошла ошибка, введите дату в формате День.Месяц.Год-День.Месяц.Год")
        bot.register_next_step_handler(message, book_data)
def potver_book(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    potver_button = types.KeyboardButton('Потвердить')
    cancel_button = types.KeyboardButton('Отменить')
    markup.add(potver_button,cancel_button)
    bot.send_message(chat_id, 'Потвердите или отмените бронь', reply_markup=markup)
    bot.register_next_step_handler(message, process_potverornot)

def process_potverornot(message):
    chat_id = message.chat.id
    if message.text.strip() == 'Потвердить':
        first_datazaezd = users[chat_id].get('first_datazaezd')
        pro_potver = "Вы успешно забронировали номер\n"
        pro_potver += f"Ваш заезд:{first_datazaed_str}\n"
        pro_potver += f"Ваш отъезд:{last_dataotezda}"
        bot.send_message(chat_id, pro_potver)
#     elif message.text.strip() == 'Отменить':
#         bot.send_message(chat_id, 'Бронь отменена', reply_markup=glavnoe_menu())


# # --- Персонал (Staff) ---
# --- Уведомление администратора ---
def notify_admin(chat_id, room_id, check_in_date, check_out_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE role = 'admin'")
    admin_ids = cursor.fetchall()
    conn.close()

    if admin_ids:
        booking_message = f"Новое бронирование!\n"
        booking_message += f"User ID: {chat_id}\n"
        booking_message += f"Room ID: {room_id}\n"
        booking_message += f"Заезд: {check_in_date}\n"
        booking_message += f"Выезд: {check_out_date}"

        for admin_id in admin_ids:
            bot.send_message(admin_id[0], booking_message)

# --- Меню персонала ---
@bot.message_handler(func=lambda message: message.text == "Меню персонала" and get_user_role(message.chat.id) == 'admin')
def staff_menu(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    view_bookings_button = types.KeyboardButton("Просмотр бронирований")
    set_availability_button = types.KeyboardButton("Управление номерами")
    markup.add(view_bookings_button, set_availability_button)
    send_message(chat_id, "Меню персонала:", markup)

@bot.message_handler(func=lambda message: message.text == "Просмотр бронирований" and get_user_role(message.chat.id) == 'admin')
def view_all_bookings(message):
    chat_id = message.chat.id
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT booking_id, user_id, room_id, check_in_date, check_out_date FROM bookings")
    bookings = cursor.fetchall()
    conn.close()

    if bookings:
        message_text = "<b>Все бронирования:</b>\n"
        for booking in bookings:
            message_text += f"ID: {booking[0]}, User ID: {booking[1]}, Room ID: {booking[2]}, Заезд: {booking[3]}, Выезд: {booking[4]}\n"
        send_message(chat_id, message_text, parse_mode="HTML")
    else:
        send_message(chat_id, "Бронирования не найдены.")

@bot.message_handler(func=lambda message: message.text == "Управление номерами" and get_user_role(message.chat.id) == 'admin')
def staff_menu_manage_rooms(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    add_room_button = types.KeyboardButton("Добавить номер")
    edit_room_button = types.KeyboardButton("Изменить номер")
    delete_room_button = types.KeyboardButton("Удалить номер")
    set_availability_button = types.KeyboardButton("Изменить доступность")
    markup.add(add_room_button,edit_room_button,delete_room_button,set_availability_button) #add all button
    send_message(chat_id, "Меню номеров:", markup)

# --- Add some test rooms -
def insert_test_rooms():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rooms")
    count = cursor.fetchone()[0]
    if count == 0:
        rooms = [
            ("VIP", 10000.00, "Luxury suite with panoramic view"),
            ("Люкс", 8000.00, "Spacious and comfortable suite"),
            ("Стандарт", 5000.00, "Cozy room with all essential amenities")
        ]
        cursor.executemany("INSERT INTO rooms (type, price, description) VALUES (?, ?, ?)", rooms)
        conn.commit()
    conn.close()
insert_test_rooms()
### Add admin users ####
ADMIN_USER_ID = 123456789  # Замените на Telegram User ID администратора
def initialize_admin(admin_user_id):  # Создаем админа
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)", (admin_user_id, 'admin'))
    conn.commit()
    conn.close()
initialize_admin(ADMIN_USER_ID)
#  Запуск бота

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
