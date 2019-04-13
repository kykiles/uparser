import os.path
import requests
from lxml import html
import re

from bot_config import ConfigBot


class ParserFilms(object):
    def __init__(self):
        ParserFilms.make_dirs()  # Создание директорий для торрент файлов если она не сущ.
        self._session = requests.Session()
        self._config = ConfigBot()
        self._HEADERS = self._config.get_dict('User-Agent')

    @staticmethod
    def make_dirs():
        _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '\\torrent_files')
        if not os.path.isdir(_path):
            os.makedirs(_path)

    @staticmethod
    def get_list_pages_codes(last_page):
        """Формирует список из параметров всех страниц с первой по последнию"""
        if not last_page:
            return
        return [n * 50 for n in range(last_page)]

    def get_html_by_url(self, f, start=None):
        """f: кодовый параметр категории фильмов, start: атрибут отвечающий за номер страницы"""
        _url = self._config.get_option('Url', 'url_viewforum')
        response = requests.get(_url, headers=self._HEADERS, params={'f': f, 'start': str(start)})
        return response.text

    def get_html_topic(self, t):
        """Получает код html страницы топика с фильмом"""
        _url = self._config.get_option('Url', 'url_viewtopic')
        response = requests.get(_url, headers=self._HEADERS, params={'t': str(t)})
        return response.text

    @staticmethod
    def get_pic_href(html_page):
        tree = html.fromstring(html_page)
        href = tree.xpath('//var[@class="postImg postImgAligned img-right"]')
        if not href:
            return
        return href[0].get('title')

    @staticmethod
    def page_text(html_page):
        """Формирует строку текста со странички с фильмом"""
        tree = html.fromstring(html_page)
        description = tree.xpath('//div[@class="post_body"]//span[@class="post-b"]')
        if not description:
            return
        temp = []
        for text in description:
            if text.text:
                temp.append(text.text.strip())
        return '\n'.join(temp)

    @staticmethod
    def searcher(html_text, regex):
        """Ищет регуляркой строку"""
        result = re.search(regex, html_text)
        if result is None:
            return
        return result.group(1).strip()

    @staticmethod
    def name_splitter(name):
        name = re.sub(r'[\\/:*?"<>|]', ' ', str(name))
        return ' '.join(name.split())

    def download_torrent_file(self, film_code, file_name):
        """Сохраняет torrent файл по ключу топика фильма с именем filename в папку torrent_files"""
        _user = {
            'login_username': self._config.get_option('User', 'login_username'),
            'login_password': self._config.get_option('User', 'login_password'),
            'login': self._config.get_option('User', 'login')
        }
        _url_login = self._config.get_option('Url', 'url_login')
        self._session.post(_url_login, headers=self._HEADERS, data=_user)

        _url_download = self._config.get_option('Url', 'url_download')
        response = self._session.get(_url_download, headers=self._HEADERS, stream=True,
                                     params={'t': film_code})

        file_name = film_code + '_' + ParserFilms.name_splitter(file_name).split('[', 1)[0]
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'torrent_files\\' + file_name + '.torrent')
        with open(path, 'bw') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return path