import json
import os.path


class JsonWorker(object):
    @staticmethod
    def dict_to_json(path, data, mode='w'):
        with open(path, mode, encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def json_to_dict(path):
        if not os.path.isfile(path):
            JsonWorker.dict_to_json(path, {})
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def search_by(keys, data):
        """Поиск в json по ключевым словам"""
        if not keys:
            return
        result = {}
        for code, value in data.items():
            flag = True
            for key in keys:
                if key.lower() not in value.get('Description').lower():
                    flag = False
            if flag:
                result[code] = value
        return result