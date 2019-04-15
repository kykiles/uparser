import os.path
from io import BytesIO, open

from configparser import ConfigParser
from multiprocessing import Pool, cpu_count

from jsonworker import JsonWorker
from engine import ParserFilms


class Services:
    def __init__(self):
        self._PATH = os.path.dirname(os.path.abspath(__file__))
        self._PARSER = ParserFilms()
        self._DATA = JsonWorker.json_to_dict('films_db.json')
        self._PICS = {}

    @staticmethod
    def config_get_option(path, section, option):
        _config = ConfigParser()
        _config.read(path)
        return _config.get(section, option)

    @staticmethod
    def sort_dict_by_value(data, row_name):
        """Сортировка значений словаря"""
        temp = {}
        sorted_by_rating = {}
        for k, v in data.items():
            temp[v[1][row_name]] = k
        for key in sorted(temp.keys(), reverse=True):
            sorted_by_rating[temp[key]] = data.get(key)
        return sorted_by_rating

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

    def get_thumbs_from_list(self, codes):
        if not codes:
            return
        with Pool(cpu_count()) as pool:
            codes_and_thumbs = pool.map(self.thumb_url, codes)
        for pic in codes_and_thumbs:
            self._PICS.update(pic)

    def get_torrent_files_from_list(self, codes):
        if not codes:
            return
        with Pool(cpu_count()) as pool:
            pool.map(self.get_path, codes)

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

    def get_pic_url_by_code(self, code):
        if code in self._PICS:
            return self._PICS.get(code)
        return self.thumb_url(code).get(code)

    def thumb_url(self, code):
        url = ParserFilms.get_pic_href(self._PARSER.get_html_topic(code))
        if not url:
            return {code: Services.get_empty_thumb_url()}
        return {code: url}

    def make_file(self, code):
        filename, received_file = self._PARSER.download_torrent_file(code, self._DATA.get(code)['Description'])
        # file = BytesIO()
        # file.write(received_file)
        # file.seek(0, 0)
        file = open(received_file)
        return file, filename

    def get_path(self, code):
        file_name = Services.file_in_directory(code, os.path.join(self._PATH, 'torrent_files'))
        if file_name:
            path = os.path.join(self._PATH, f'torrent_files\\{file_name}')
        else:
            path = self._PARSER.download_torrent_file(code, self._DATA.get(code)['Description'])
        return path

    def get_name_by_code(self, code):
        return self._DATA.get(code)

    def get_films_db_data(self):
        return self._DATA

    def get_pics_url_data(self):
        return self._PICS

    def top250(self):
        top250 = JsonWorker.json_to_dict(os.path.join(self._PATH, 'films_with_rating.json'))
        return top250