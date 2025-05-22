import telebot
from telebot import types
import datetime

Bot_Token = '7504411607:AAF94hIkBCH_zzbWGD-ePQP2OTzZCDx6UQI'
bot = telebot.TeleBot(Bot_Token)
users = {}
booking ={}
room_types = {
    'Стандарт': {
        'describe': ' Уютный номер, Wi-Fi, Телевизор, Кофемашина, Отдельная ванна',
        'price руб/сут': 4500,
        'dostup': 10
    },
    'Люкс': {
        'describe': 'Просторный номер с гостиной зоной, Wi-Fi, Телевизор, Кофемашина, Мини-Бар, Отдельная ванна',
        'price руб/сут': 9500,
        'dostup': 5
    },
    'VIP': {
        'describe': 'Эксклюзивный номер с панорамным видом с VIP-лаунж зоной Wi-Fi, Телевизор, Кофемашина, Мини-Бар, Отдельная ванна',
        'price руб/сут': 15000,
        'dostup': 3
    }
}
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
    users[chat_id] = {'role:guest'}
    bot.send_message(chat_id, "Добро пожаловать, здесь можно сделать бронирование номера!", reply_markup=markup)
    users[chat_id] = 'guest'
@bot.message_handler(func=lambda message: message.text in ['Забронировать номер','Отменить бронь'] and users.get(message.chat.id) == 'guest')
def menu_booking(message):
    chat_id = message.chat.id
    if message.text.strip() == 'Забронировать номер':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        vip_button = types.KeyboardButton("VIP:Эксклюзивный номер")
        lux_button = types.KeyboardButton("Люкс:Просторный номер")
        standart_button = types.KeyboardButton("Стандарт: Уютный номер")
        markup.add(vip_button, lux_button, standart_button)
        bot.send_message(chat_id, "Пожалуйста, выберете какой номер вы хотите",reply_markup = markup)
    elif message.text.strip() == 'Отменить бронь':
        bot.send_message(chat_id, 'Бронь отменена', reply_markup = glavnoe_menu())
@bot.message_handler(func=lambda message: message.text in ['VIP','Люкс', 'Стандарт'])
def choiced_room(message):
    chat_id = message.chat.id
    room = message.text.strip()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if room in room_types:
        users[chat_id] = {'room_type': room}
    if room == 'VIP':
        bot.send_message(chat_id, 'Вы выбрали VIP-номер ')
    elif room == "Люкс":
        bot.send_message(chat_id, 'Вы выбрали Люкс-номер')
    elif room == 'Стандарт':
        bot.send_message(chat_id, 'Вы выбрали Стандарт - номер')
    bot.send_message(chat_id, 'Укажите дату заезда и дату отъезда в формате-День.Месяц.Год - День.Месяц.Год')
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
        booking[chat_id] = {
            'first_datazaezd': first_datazaezd,
            'last_dataotezd': last_dataotezd
        }
        potver_book(message)
    except ValueError:
        bot.send_message(chat_id, "Произошла ошибка, введите дату в формате День.Месяц.Год - День.Месяц.Год")
        bot.register_next_step_handler(message, book_data)
def potver_book(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    potver_button = types.KeyboardButton('Потвердить')
    cancel_button = types.KeyboardButton('Отменить')
    markup.add(potver_button,cancel_button)
    bot.send_message(chat_id, 'Потвердите или отмените', reply_markup=markup)
    bot.register_next_step_handler(message, process_potverornot)

def process_potverornot(message):
    chat_id = message.chat.id
    if message.text.strip() == 'Потвердить':
        if chat_id in users and 'room_type' in users[chat_id] and chat_id in booking:
            room_type = users[chat_id]['room_type']
            room_info = room_types[room_type]
            first_datazaezd = booking[chat_id]['first_datazaezd']
            last_dataotezd = booking[chat_id]['last_dataotezd']
            bot.send_message(chat_id, f'Ваше бронирование подтверждено:\n'
                                      f'Тип номера: {room_type}\n'
                                      f'Описание номера: {room_info["describe"]}\n'
                                      f'Дата заезда: {first_datazaezd.strftime("%d.%m.%Y")}\n'
                                      f'Дата отъезда: {last_dataotezd.strftime("%d.%m.%Y")}')

    elif message.text.strip() == 'Отменить':
        bot.send_message(chat_id, 'Бронь отменена', reply_markup=glavnoe_menu())
# # --- Персонал (Staff) ---
@bot.message_handler(func=lambda message: message.text == "Меню персонала" )
def staff_menu(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    view_bookings_button = types.KeyboardButton("Просмотр бронирований")
    set_availability_button = types.KeyboardButton("Управление номерами")
    markup.add(view_bookings_button, set_availability_button)
    bot.send_message(chat_id, "Меню персонала:", markup)
@bot.message_handler(func=lambda message: message.text == "Управление номерами" )
def staff_menu_manage_rooms(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    add_room_button = types.KeyboardButton("Добавить номер")
    delete_room_button = types.KeyboardButton("Удалить номер")
    markup.add(add_room_button,delete_room_button)
    bot.send_message(chat_id, "Меню номеров:", markup)

@bot.message_handler(func=lambda message: message.text == "Добавить номер")
def add_room(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите, то что хотите добавить")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling(none_stop=True)
