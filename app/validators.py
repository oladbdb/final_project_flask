import re

def validate_user_form(data, check_password=True):
    errors = {}

    username = data.get('username', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()

    if not username:
        errors['username'] = "Поле логин не может быть пустым."
    elif len(username) < 5 or not re.fullmatch(r'[A-Za-z0-9]+', username):
        errors['username'] = "Логин должен содержать только латинские буквы и цифры, не менее 5 символов."

    if not first_name:
        errors['first_name'] = "Поле имя не может быть пустым."

    if not last_name:
        errors['last_name'] = "Поле фамилия не может быть пустым."

    if check_password:
        if not password:
            errors['password'] = "Пароль не может быть пустым."
        elif len(password) < 8:
            errors['password'] = "Пароль должен быть не менее 8 символов."
        elif len(password) > 128:
            errors['password'] = "Пароль должен быть не более 128 символов."
        elif ' ' in password:
            errors['password'] = "Пароль не должен содержать пробелы."
        elif not re.search(r'[A-ZА-Я]', password):
            errors['password'] = "Пароль должен содержать хотя бы одну заглавную букву."
        elif not re.search(r'[a-zа-я]', password):
            errors['password'] = "Пароль должен содержать хотя бы одну строчную букву."
        elif not re.search(r'[0-9]', password):
            errors['password'] = "Пароль должен содержать хотя бы одну цифру."
        elif not re.fullmatch(r"[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+\(\)\[\]{}><\/\\|\"'\.,:]+", password):
            errors['password'] = "Пароль содержит недопустимые символы."

    return errors
