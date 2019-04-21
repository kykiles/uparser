import requests
from lxml import html
import re

from bot_config import ConfigBot


class ParserFilms(object):
    def __init__(self):
        self._session = requests.Session()
        self._config = ConfigBot()
        self._HEADERS = self._config.get_dict('User-Agent')

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
        response = self._session.get(_url_download, headers=self._HEADERS,
                                     params={'t': film_code})

        # file_name = film_code + '_' + ParserFilms.name_splitter(file_name).split('[', 1)[0]
        return file_name, response.content