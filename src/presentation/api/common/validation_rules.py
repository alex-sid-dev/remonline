"""
Правила валидации полей — единый источник для Pydantic-схем и для отдачи на фронт.
Фронт использует те же ограничения и сообщения, что и бэкенд.
"""

# Пароль (RegisterSchema, LoginSchema)
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 10
PASSWORD_SPECIAL_CHARACTERS = "!@#$%^&*(),.?\":{}|<>_-+[]=\\/"

PASSWORD_MESSAGES = {
    "required": "Введите пароль",
    "length": f"Пароль от {PASSWORD_MIN_LENGTH} до {PASSWORD_MAX_LENGTH} символов",
    "digit": "Пароль должен содержать хотя бы одну цифру",
    "uppercase": "Пароль должен содержать хотя бы одну заглавную букву",
    "special": f"Пароль должен содержать хотя бы один спецсимвол: {PASSWORD_SPECIAL_CHARACTERS}",
}

# Email (EmailStr)
EMAIL_MESSAGE = "Некорректный формат email"

# Телефон (validate_phone — phonenumbers RU: только +7 и ровно 10 цифр)
PHONE_PATTERN = r"^\+7\d{10}$"
PHONE_MESSAGE = "Not valid phone number. Expected format: +78008008000"

# ФИО (обязательное непустое)
FULL_NAME_REQUIRED_MESSAGE = "Введите ФИО"


def get_validation_rules_for_frontend() -> dict:
    """Правила и сообщения для фронтенда (совпадают с Pydantic-валидацией)."""
    return {
        "password": {
            "min_length": PASSWORD_MIN_LENGTH,
            "max_length": PASSWORD_MAX_LENGTH,
            "special_characters": PASSWORD_SPECIAL_CHARACTERS,
            "messages": PASSWORD_MESSAGES,
        },
        "email": {
            "message": EMAIL_MESSAGE,
        },
        "phone": {
            "pattern": PHONE_PATTERN,
            "message": PHONE_MESSAGE,
        },
        "full_name": {
            "message": FULL_NAME_REQUIRED_MESSAGE,
        },
    }
