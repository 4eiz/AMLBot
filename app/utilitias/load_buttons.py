import json



json_path = 'app/utilitias/buttons.json'
with open(json_path, 'r', encoding='utf-8') as file:
    buttons = json.load(file)




def get_button(keyboard, button, lang="ru", buttons=buttons, **kwargs):
    """Возвращает текст кнопки по названию клавиатуры и кнопки, если они существуют."""
    keyboard_data = buttons.get(keyboard)
    if keyboard_data:
        button_data = keyboard_data.get(button)
        if button_data:
            template = button_data.get(lang, f"Message not available in '{lang}' language.")
            try:
                return template.format(**kwargs)
            except KeyError as e:
                return f"Missing parameter for message '{keyboard}.{button}': {e}"
        else:
            return f"Button '{button}' not found in keyboard '{keyboard}'."
    else:
        return f"Keyboard '{keyboard}' not found."