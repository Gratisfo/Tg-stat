import sqlite3 as sq

db = sq.connect('tg_stat.db')
cur = db.cursor()


def create_new_db():
    """
    Создаем новую Базу Данных с 2 таблицами: channels и posts
    """
    cur.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_link TEXT,
            average_post_reach INTEGER,
            participant_count INTEGER,                                                                  
            median_share REAL,
            lower_bound REAL,
            upper_bound REAL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_link TEXT,
            post_link REAL,
            shares INTEGER,
            post_date DATE,
            viral BOOLEAN
        )
    ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS virality_params (
                    x INTEGER,
                    shares_limit INTEGER
                )
            ''')

    db.commit()


def get_virality_params():
    """
    Достаем из базы параметры вирусности
    """
    cur.execute('SELECT x, shares_limit FROM virality_params LIMIT 1')
    x_value, share_limit_value = cur.fetchone()
    return x_value, share_limit_value


def update_virality_params(x, shares):
    """
        Удаляем старые данные с параметрами
        вирусности и добавляем новые
    """
    cur.execute('DELETE FROM virality_params')

    cur.execute('''
                    INSERT INTO virality_params (x, shares_limit)
                    VALUES (?, ?)
                ''', (x, shares))

    # Сохраняем изменения и закрываем соединение
    db.commit()


def get_all_channel_links():
    """
    Получаем все ссылки каналов
    """
    # Выбираем все значения из колонки channel_link в таблице channels_list
    cur.execute('SELECT DISTINCT channel_link FROM channels')
    result = cur.fetchall()

    # Преобразуем полученный список кортежей в простой массив
    channel_links = [row[0] for row in result]

    print(channel_links)
    return channel_links


def insert_or_update_channel(channel_link, average_post_reach, participant_count):
    # Проверяем, существует ли запись с данным channel_link
    cur.execute('SELECT * FROM channels WHERE channel_link = ?', (channel_link,))
    existing_record = cur.fetchone()

    if existing_record:
        # Если запись существует, обновляем значения
        cur.execute('''
               UPDATE channels
               SET average_post_reach = ?, participant_count = ?
               WHERE channel_link = ?
           ''', (average_post_reach, participant_count, channel_link))
    else:
        # Если запись не существует, вставляем новую запись
        cur.execute('''
               INSERT INTO channels (channel_link, average_post_reach, participant_count)
               VALUES (?, ?, ?)
           ''', (channel_link, average_post_reach, participant_count))

    # Сохраняем изменения и закрываем соединение
    db.commit()


def update_posts(channel_link, posts_link, shares, post_date, viral):
    """
    Удаляем старые данные о постах из таблицы
    и загружаем новые данные о постах
    """
    cur.execute('DELETE FROM posts')

    # Перебираем ключи и значения словаря и вставляем их в таблицу posts

    cur.execute('''
                INSERT INTO posts (channel_link, post_link, shares, post_date, viral)
                VALUES (?, ?, ?, ?, ?)
            ''', (channel_link, posts_link, shares, post_date, viral))

    # Сохраняем изменения и закрываем соединение
    db.commit()


if __name__ == '__main__':
    create_new_db()
    # обновление параметров вирусноти 
    # 3 - X от среднего
    # 30 - минимальное число пересылок
    update_virality_params(3, 30)
