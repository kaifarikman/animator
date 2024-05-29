from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import asyncio
import aioschedule
import config
import keyboards
import db
import date
import datetime


class CreateEvent(StatesGroup):
    event_name = State()
    event_organization = State()
    event_data = State()
    event_time = State()
    event_price = State()
    event_location = State()
    action = State()


storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot=bot, storage=storage)
white_users = config.white_users
admin = config.admin
user = config.user
watch_user = config.watch_user
watch_users = config.watch_users
check_data = r'\d{2}\.\d{2}.\d{4}'
check_time = r'\d{2}\:\d{2}'


@dp.message_handler(filters.IDFilter(user_id=white_users), commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я умею создавать кучу событий и напоминать тебе об этом\n'
                         'Попробуем? Напиши /help и все узнаешь🕰', reply_markup=keyboards.started)


@dp.message_handler(filters.IDFilter(user_id=watch_user), commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я умею создавать кучу событий и напоминать тебе об этом.\n'
                         'Попробуем? Напиши /help и все узнаешь🕰', reply_markup=keyboards.started_user)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('отменено', reply_markup=keyboards.started)


@dp.message_handler(filters.IDFilter(user_id=white_users), commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer(text='У нас с тобой есть парочка функций:\n'
                              '/create - создать событие\n'
                              '/cancel - отменить действие(рпи создании события)\n'
                              '/today - события сегодня\n'
                              '/tomorrow - сообытия завтра\n'
                              '/nearest - ближайщее событие\n', reply_markup=keyboards.remove)


@dp.message_handler(filters.IDFilter(user_id=white_users), commands=['create'], state='*')
async def create_event(message: types.Message):
    date.check_data()
    await CreateEvent.event_name.set()
    await message.answer('Напиши название мероприятия', reply_markup=keyboards.remove)


@dp.message_handler(lambda x: not x.text, state=CreateEvent.event_name)
async def wrong_name(message: types.Message):
    return await message.answer('ты ввел что-то другое')


@dp.message_handler(lambda x: x.text, state=CreateEvent.event_name)
async def good_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_name'] = message.text
    await CreateEvent.next()
    await message.answer('Напиши название своей компании', reply_markup=keyboards.organizations)


@dp.message_handler(state=CreateEvent.event_organization)
async def add_organization(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_organization'] = message.text

    await CreateEvent.next()
    await message.answer('Какого числа у тебя будет заказ?(дд.мм.гггг)', reply_markup=keyboards.remove)


@dp.message_handler(filters.Regexp(check_data), state=CreateEvent.event_data)
async def add_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_data'] = message.text

    await CreateEvent.next()
    await message.answer('В какое время у тебя будет заказ?', reply_markup=keyboards.remove)


@dp.message_handler(state=CreateEvent.event_time)
async def add_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_time'] = message.text

    await CreateEvent.next()
    await message.answer('Какую зарплату ты получаешь с заказа?', reply_markup=keyboards.remove)


@dp.message_handler(lambda message: not message.text.isdigit(), state=CreateEvent.event_price)
async def failed_price(message: types.Message):
    return await message.answer(
        'ну это не цифры, значит введи заново и правильно пожалуйста')  # если цена записана не цифрами


@dp.message_handler(lambda message: message.text.isdigit(), state=CreateEvent.event_price)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(event_price=int(message.text))
    await CreateEvent.next()
    await message.answer('Отправь адрес проведения',
                         reply_markup=keyboards.remove)


@dp.message_handler(state=CreateEvent.event_location)
async def add_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_location'] = message.text
    await CreateEvent.next()
    s = f'Название события: {data["event_name"]}\n' \
        f'Организация: {data["event_organization"]}\n' \
        f'Дата проведения: {data["event_data"]}\n' \
        f'Время проведения: {data["event_time"]}\n' \
        f'Цена: {data["event_price"]}\n' \
        f'Место проведения: {data["event_location"]}\n'
    await message.answer(s, reply_markup=keyboards.remove)
    await message.answer('Вы согласны с введнными данными?',
                         reply_markup=keyboards.yes_no)


@dp.message_handler(state=CreateEvent.action)
async def action(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = message.text
    if data['action'].lower() == 'да':
        event = [data['event_name'], data['event_organization'], data['event_data'], data['event_time'],
                 data['event_price'], data['event_location']]
        db.add_event(event)
        await message.answer('успешно добавлено', reply_markup=keyboards.started)
    else:
        await message.answer('мы удалили введнные данные', reply_markup=keyboards.started)
    await state.finish()


@dp.message_handler(filters.IDFilter(user_id=white_users), commands=['overlook'])  # Inline - миша подсказал
async def overlook(message: types.Message):
    loc = ''
    # lst = db.get_locations()
    lst = []
    for i in range(len(lst)):
        loc += f'{i + 1}) {lst[i][0]}\n'
    await message.answer('не добавлено')


@dp.message_handler(filters.IDFilter(user_id=white_users), commands=['nearest'])
async def nearest(message: types.Message):
    date.check_data()
    try:
        row, time_of_nearest_event = date.nearest_event()
        time_of_nearest_event = str(time_of_nearest_event)
        event = db.all_events()[-1]
        if len(time_of_nearest_event.split()) == 1:
            day = 'Через'
        else:
            day = 'Через ' + str(time_of_nearest_event.split()[0]) + 'дн,'
        time_of_near = time_of_nearest_event.split()[-1].split('.')[0].split(':')
        nearest_event = f'{day} {time_of_near[0]}час {time_of_near[1]}мин {time_of_near[2]}сек у вас будет мероприятие. ' \
                        f'Информация о мероприятии:\n' \
                        f'Название события: {event[1]}\n' \
                        f'Организация: {event[2]}\n' \
                        f'Дата проведения: {event[3]}\n' \
                        f'Время проведения: {event[4]}\n' \
                        f'Цена: {event[5]}\n' \
                        f'Место проведения: {event[6]}\n'
        await message.answer(nearest_event, reply_markup=keyboards.started)
    except:
        await message.answer(
            'Возникла ошибка, которая скорее всего связана с тем, что вы не создали еще ни одного события!')


@dp.message_handler(filters.IDFilter(user_id=watch_users + [user]), commands=['today'])
async def today(message: types.Message):
    time_now = '.'.join(str(datetime.datetime.now()).split()[0].split('-')[::-1])
    s, suma = date.defer(time_now)
    await message.answer(s)
    if suma:
        await message.answer(f'Итого за {time_now} вы получите: {suma}₽')


@dp.message_handler(filters.IDFilter(user_id=watch_users + [user]), commands=['tomorrow'])
async def tomorrow(message: types.Message):
    time_now = '.'.join(str(datetime.date.today() + datetime.timedelta(days=1)).split('-')[::-1])
    s, suma = date.defer(time_now)
    await message.answer(s)
    if suma:
        await message.answer(f'Итого за {time_now} вы получите: {suma}₽')


@dp.message_handler(filters.IDFilter(user_id=white_users), filters.Regexp(check_data))
async def random_data(message: types.Message):
    time_now = message.text
    s, suma = date.defer(time_now)
    await message.answer(s)
    if suma:
        await message.answer(f'Итого за {time_now} вы получите: {suma}₽')


@dp.message_handler(filters.IDFilter(user_id=watch_users), commands=['admin'])
async def admin(message: types.Message):
    await message.answer('что умеет админ?', reply_markup=keyboards.admin)


@dp.message_handler(commands=['all_events'])
async def all_ev(message: types.Message):
    events = ''
    for i in db.all_events():
        id_id = i[0]
        date_date = ' '.join(i[3:5])
        s = f'{id_id}) {date_date} - {i[1]}({i[2]} - {i[6]}). price = {i[5]}\n'
        events += s
    if not events:
        events = '0 событий'
    await message.answer(events)


# банальная проверка
@dp.message_handler()
async def evening_output(message: types.Message):
    await message.answer('я тебя не понимаю, ты наверное ошибся')


# отправка сообщений по времени неправильно
async def morning_reminder():
    time_now = '.'.join(str(datetime.datetime.now()).split()[0].split('-')[::-1])
    s, suma = date.defer(time_now)
    await bot.send_message(chat_id=user, text=s)


async def evening_reminder():
    await asyncio.sleep(1)
    now = datetime.datetime.now()
    time_now = '.'.join(str(now).split()[0].split('-')[::-1])
    s, suma = date.defer(time_now)
    current_time = now.strftime("%H:%M:%S")
    if current_time == '22:30:00':
        await bot.send_message(chat_id=user, text=f'Итого за весь день вы получили: {suma}₽')


async def scheduler():
    aioschedule.every().day.at("06:00").do(morning_reminder)
    aioschedule.every().day.at("00:00").do(evening_reminder)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    db.start_db()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
