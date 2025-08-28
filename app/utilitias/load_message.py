import json
import os


json_path = 'app/utilitias/messages.json'
file = open(json_path, 'r', encoding='utf-8')
messages = json.load(file)


def get_message(code, lang="ru", messages=messages, **kwargs):
    """Возвращает сообщение по коду и языку. Если не найдено, возвращает ошибку."""
    if code in messages:
        template = messages[code].get(lang, f"Message not available in '{lang}' language.")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Missing parameter for message '{code}': {e}"

    return f"Message with code '{code}' not found."