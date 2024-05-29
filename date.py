import datetime as dt
import db


def check_data():
    date_now = dt.datetime.strptime(str(dt.datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
    events = reissue_event()
    for k, v in events.items():
        event_data = dt.datetime.strptime(v[0], '%d.%m.%Y %H:%M:%S.%f')
        difference = (event_data - date_now).total_seconds()
        total = int(str(difference).split('.')[0])
        if total < 0:
            db.delete_event(int(k))


def nearest_event():
    date_now = dt.datetime.strptime(str(dt.datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
    events = reissue_event()
    lst = []
    for k, v in events.items():
        event_data = dt.datetime.strptime(v[0], '%d.%m.%Y %H:%M:%S.%f')
        difference = (event_data - date_now).total_seconds()
        total = int(str(difference).split('.')[0])
        lst.append([total, int(k), (event_data - date_now)])
    minim = 9 * 10 ** 9
    for i in lst:
        if i[0] < minim:
            minim = i[0]
    for i in lst:
        if i[0] == minim:
            return i[1:]


def reissue_event():
    events = db.all_events()
    d = dict()
    for i in events:
        date = f"{' '.join(i[3:5])}:00.000000"
        ev = [i[1]] + i[5:]
        d[i[0]] = [date, ev]
    return d


def events_at_a_certain_moment(s):
    check_data()
    events = db.all_events()
    moment = list()
    for i in events:
        if i[3] == s:
            moment.append([i[4], [i[1], i[2], i[5]]])
    sorted_moment = sorted(moment, key=lambda x: tuple(map(int, x[0].split(":"))))
    return sorted_moment


def defer(time_now):
    lst = events_at_a_certain_moment(time_now)
    if not lst:
        s = f'вы свободны, но бедны.\n' \
            f'{time_now} у вас нет ни одного заказа!'
        return s, 0
    suma = 0
    s = f'{time_now} - {len(lst)} заказ(а, ов)\n'
    for i in lst:
        s += f'в {i[0]} - {i[1][0]} от {i[1][1]}(цена {i[1][2]})\n'
        suma += int(i[1][2])
    return s, suma
