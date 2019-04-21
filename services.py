import os.path
from io import BytesIO

from configparser import ConfigParser

from jsonworker import JsonWorker
from engine import ParserFilms


class Services:
    def __init__(self):
        self._PATH = os.path.dirname(os.path.abspath(__file__))
        self._PARSER = ParserFilms()
        self._DATA = JsonWorker.json_to_dict('films_db.json')

    @staticmethod
    def config_get_option(path, section, option):
        _config = ConfigParser()
        _config.read(path)
        return _config.get(section, option)

    @staticmethod
    def counter_result_search(data, count=5):
        if not data:
            return
        result = {}
        temp = {}
        keys = list(data.keys())
        n = 1
        for i in range(len(keys)):
            key = keys[i]
            temp[key] = data.get(key)
            if (i + 1) % count == 0:
                result[n] = temp
                temp = {}
                n += 1
        result[n] = temp
        return result

    @staticmethod
    def description_splitter(description, symbol):
        result = description.split(symbol, 1)
        if len(result) < 2:
            return description, 'Краткое описание отсутствует'
        return result[0], f'({result[1]}'

    @staticmethod
    def poster(url):
        return f'<a href="{url}">&#8205;</a>'

    def search(self, words):
        if not words:
            return
        keys = words.split(' ')
        keys = list(filter(None, keys))
        result = JsonWorker.search_by(keys, self._DATA)
        if not result:
            return
        return result

    @staticmethod
    def file_in_directory(code, path):
        files = os.listdir(path)
        for file_name in files:
            if code in file_name:
                return file_name

    @staticmethod
    def get_empty_thumb_url():
        return 'https://t3.ftcdn.net/jpg/01/01/89/46/240_F_101894688_RVSZUtDfPR6Cr5eBDQI7Qo5pZ01jmyK3.jpg'

    def make_file(self, code):
        filename, received_file = self._PARSER.download_torrent_file(code, self._DATA.get(code)['Description'])
        file = BytesIO()
        file.name = f'{filename}.torrent'
        file.write(received_file)
        file.seek(0, 0)
        return file

    def get_name_by_code(self, code):
        return self._DATA.get(code)

    def top250(self):
        top250 = JsonWorker.json_to_dict(os.path.join(self._PATH, 'films_with_rating.json'))
        return top250