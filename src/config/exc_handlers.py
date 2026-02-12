from fastapi import FastAPI
from src.application.errors._base import ApplicationError
from src.presentation.api.common.exc_handlers import application_error_handler

def setup_exc_handlers(app: FastAPI) -> None:
    # Регистрируем единый обработчик для базового класса всех ошибок приложения
    app.add_exception_handler(ApplicationError, application_error_handler)
