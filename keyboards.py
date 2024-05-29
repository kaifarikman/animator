from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

organizations = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
organizations.add("Пряники", "КиндерГрад", "Умные Шоу")
organizations.add("Моя Радость", "Выход: Квест комната")
started = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
started.add('/start', '/help')
started.add('/create', '/nearest')
started.add('/today', '/tomorrow')
remove = ReplyKeyboardRemove()
yes_no = ReplyKeyboardMarkup(resize_keyboard=True,
                             one_time_keyboard=True)  # просто обычная клавиатура
y_n1, y_n2 = KeyboardButton('да'), KeyboardButton('нет')
yes_no.add(y_n1, y_n2)  # добавление в обычную клавиатуру

admin = ReplyKeyboardMarkup(resize_keyboard=True,
                            one_time_keyboard=True)
admin.add('/all_events')

started_user = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
started_user.add('/today', '/tomorrow')
started_user.add('/all_events')