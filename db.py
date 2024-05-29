import sqlite3


def start_db():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute('''create table if not exists events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        organization TEXT,
        data TEXT,
        time TEXT,
        price INTEGER,
        location TEXT)''')
    cur.close()
    conn.commit()


def event_length():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    length = len(cur.execute('select id from events').fetchall())
    cur.close()
    conn.commit()
    return length


def add_event(event):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute('''insert into events (name, organization, data, time, price, location) values(?, ?, ?, ?, ?, ?)''',
                event)
    cur.close()
    conn.commit()


def delete_event(row):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute(f'delete from events where id = {row}')  # удаляет то, чего нет, что хочет(возвращает всегда true)
    events = cur.execute('''select name, organization, data, time, price, location from events''').fetchall()
    cur.execute('delete from events')
    count = 1
    for event in events:
        tup = (count, *event)
        cur.execute('''insert into events (id, name, organization, data, time, price, location) values(?, ?, ?, ?, ?, ?, ?)''',
                    tup)
        count += 1
    cur.close()
    conn.commit()


def all_events():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    events = list()
    for i in cur.execute('''select id, name, organization, data, time, price, location from events''').fetchall():
        events.append(list(i))
    cur.close()
    conn.commit()
    return events


def check_last_event():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    last_event = list(
        cur.execute('''select max(id), name, organization, data, time, price, location from events''').fetchone())
    cur.close()
    conn.commit()
    return last_event


def delete_last_event():
    delete_event(event_length())
