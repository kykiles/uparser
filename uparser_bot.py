from random import choice
import os

import telebot
from telebot import types
from flask import Flask, request

from services import Services

# 📽️
# bot = telebot.TeleBot(Services.config_get_option('config.ini', 'Token', 'token'))

TOKEN = Services.config_get_option('config.ini', 'Token', 'token')
bot = telebot.AsyncTeleBot(TOKEN)
server = Flask(__name__)


def create_inline_button(label, callback_data=None, url=None, query=None):
    return telebot.types.InlineKeyboardButton(text=label,
                                              callback_data=callback_data,
                                              url=url,
                                              switch_inline_query=query)


def create_inline_row(row_width, *buttons):
    markup = telebot.types.InlineKeyboardMarkup(row_width=row_width)
    markup.row(*buttons)
    return markup


def random_film(data):
    random_choice = choice(list(data.keys()))
    len_result = str(len(data))
    return random_choice, len_result


def film_poster(code, description=None):
    if not description:
        description = services.get_name_by_code(code)
    if not description:
        return
    downloads = description.get('Downloads')
    seeders = description.get('Seeders')
    leechers = description.get('Leechers')
    gb = description.get('GB')
    download_btn = create_inline_button('💾', f'download_{code}')
    url = f"{services.config_get_option('config.ini', 'Url', 'url_viewtopic')}?t={code}"
    pic_url = description.get('pic_url')
    description_btn = create_inline_button('🔎', f'description_{code}', url=url)
    download_markup = create_inline_row(2, description_btn, download_btn)

    return {
        code:
            {
                'Description': description.get('Description'),
                'Downloads': downloads,
                'Seeders': seeders,
                'Leechers': leechers,
                'GB': gb,
                'Markup': download_markup,
                'Pic': pic_url
            }
    }


def switch_query(inline_query, default=None):
    offset = inline_query.offset
    if default:
        result = services.top250()
    else:
        result = services.search(inline_query.query)

    rd_film = random_film(result)
    result = services.counter_result_search(result, 5)
    r = []  # Список результата запроса

    if not result:
        url = services.get_empty_thumb_url()
        r.append(types.InlineQueryResultArticle('Empty',
                                                'По вашему запросу ничего не найдено',
                                                types.InputTextMessageContent('Ничего не найдено...'),
                                                description='Измените параметры поиска',
                                                thumb_url=url))
        bot.answer_inline_query(inline_query.id, [*r])
        return

    if offset:
        if len(offset) < len(result):
            offset += '1'
        elif len(offset) == len(result):
            return
    else:
        offset = '1'

    page = result[len(offset)]

    for code, description in page.items():
        description = film_poster(code, description)[code]
        url = f"{services.config_get_option('config.ini', 'Url', 'url_viewtopic')}?t={code}"
        name, other = services.description_splitter(description.get('Description'), '(')
        pic_url = description.get('Pic')
        downloads = description.get('Downloads')
        seeders = description.get('Seeders')
        leechers = description.get('Leechers')
        gb = description.get('GB')

        other = f'Скачиваний: {downloads}\n' \
            f'Сиды: {seeders} Личи: {leechers}\n' \
            f'Размер: {gb}'
        input_text_message = types.InputTextMessageContent(f'📽️ {services.poster(pic_url)}'
                                                           f'{description.get("Description")}\n\n'
                                                           f'<i>Скачиваний: {downloads}</i>\n'
                                                           f'<i>Сиды: {seeders}</i>\n'
                                                           f'<i>Личи: {leechers}</i>\n'
                                                           f'<i>Размер: {gb}</i>',
                                                           parse_mode='HTML')
        r.append(types.InlineQueryResultArticle(code,
                                                name,
                                                input_text_message,
                                                description=other,
                                                url=url,
                                                hide_url=True,
                                                thumb_url=pic_url,
                                                reply_markup=description['Markup']))

    bot.answer_inline_query(inline_query.id, [*r], next_offset=offset,
                            switch_pm_text=f'Найдено результатов: {rd_film[1]}',
                            switch_pm_parameter=rd_film[0])


@bot.message_handler(commands=['start'])
def start_option(message):
    query = message.text.split(' ', 1)
    if len(query) == 2:
        code = query[1]
        description = film_poster(code)[code]
        pic_url = description.get('Pic')
        bot.send_message(message.chat.id,
                         f'📽️ {services.poster(pic_url)}'
                         f'{description.get("Description")}\n\n'
                         f'<i>Скачиваний: {description.get("Downloads")}</i>\n'
                         f'<i>Сиды: {description.get("Seeders")}</i>\n'
                         f'<i>Личи: {description.get("Leechers")}</i>\n'
                         f'<i>Размер: {description.get("GB")}</i>',
                         parse_mode='HTML',
                         reply_markup=description.get("Markup")).wait()
        return

    start_btn = create_inline_button('ПОИСК', query='')
    markup = create_inline_row(1, start_btn)
    bot.send_message(message.chat.id,
                     'Привет, давай подберём фильм для тебя? Для справки жми /help',
                     reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_option(message):
    help_text = 'Для того чтобы найти фильм нажмите /start. Либо введите в любом чате @UParserBot после чего введите ' \
                'через пробел ключевые слова для поиска. Например: 2012 Ужасы США HDRip '
    bot.send_message(message.chat.id, help_text)


@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    switch_query(inline_query)


@bot.inline_handler(lambda query: len(query.query) is 0)
def default_query(inline_query):
    switch_query(inline_query, True)


@bot.callback_query_handler(func=lambda call: True)
def callback_download(call):
    if not call.data:
        return
    code = call.data.split('_')[1]
    if 'download_' in call.data:
        torrent = services.make_file(code)
        bot.send_document(call.from_user.id, torrent).wait()


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://uparser.herokuapp.com/' + TOKEN)
    return "OK!", 200


if __name__ == '__main__':
    services = Services()
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))