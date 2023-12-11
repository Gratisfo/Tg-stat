import requests
import json
import time
from config import token
from db_functions import *

# TODO: разобраться как не дублировать посты с картинками проверка в get_one_post
# TODO: протестировать как работает определение вирусности


def test_post_virality(shares, avg_post_reach):
    """ Достаем параметры вирусности поста и проверяем пост
    Возвращаем True есть пост вирусный, и False если нет"""
    if avg_post_reach > 0:
        x, share_limit = get_virality_params()
        return shares / avg_post_reach >= x and shares > share_limit
    else:
        return False


def get_one_post(post_link, avg_post_reach):
    """
    Достаем статистику по пересылкам поста
    """
    post_stat = f'https://api.tgstat.ru/posts/stat?' \
                f'token={token}&postId={post_link}'
    response = requests.get(post_stat)
    data = json.loads(response.text)
    post_date = data['response']['views'][0]['date'] # достаем дату публикации
    shares_count = data['response']['sharesCount']
    viral = test_post_virality(shares_count, avg_post_reach)
    print(post_link, post_date, viral, shares_count)
    return shares_count, post_date, viral


def get_posts(channel, days, avg_post_reach):
    """
    Получаем все посты и их стату из канала за последние N дней
    """
    end_time = int(time.time())
    start_time = end_time - (days * 24 * 60 * 60)

    channel_posts = f'https://api.tgstat.ru/channels/posts?' \
                    f'token={token}&channelId={channel}&startTime={start_time}' \
                    f'&endTime={end_time}&hideForwards=1&hideDeleted=1'
    response = requests.get(channel_posts)

    data = json.loads(response.text)

    # получаем ссылки на посты
    post_links = [item['link'] for item in data['response']['items']]

    # собираем статистику по постам
    for post_link in post_links:
        shares, date, viral = get_one_post(post_link, avg_post_reach)
        # записываем данные в БД
        update_posts(channel, post_link, shares, date, viral)

    print('Получили ссылки на посты и стату по ним', channel)


def get_channel_info(channel, days):
    """
    Делаем запрос по каналу, запуск ф-ций по постам,
    определению вирусных публицакаций
    """
    # TODO: эта же функция будет запускаться при добавлении нового канала
    channel_info = f'https://api.tgstat.ru/channels/stat?token={token}&channelId={channel}'
    response = requests.get(channel_info)
    try:
        data = json.loads(response.text)
        avg_post_reach = data['response']['avg_post_reach']
        participants_count = data['response']['participants_count']
        print('получили основную инфу по каналам')

        # записываем в БД полученные данные о каналах
        insert_or_update_channel(channel, avg_post_reach, participants_count)
        print('Получили всю инфу, добавили в бд')

        # обновляем данные о постах
        get_posts(channel, days, avg_post_reach)
        print('Получили всю инфу, добавили в бд')

    except KeyError:
        print("Response error:", response.status_code)


if __name__ == '__main__':
    # telegram_channels = get_all_channel_links()
    telegram_channels = ["https://t.me/kudahiko", "https://t.me/andrey_pro_business"] # тест для одного канала, тк в базе пока пусто
    days = 1
    for channel in telegram_channels:
        print('Начали обрабатывать канал: ', channel)
        get_channel_info(channel, days)

