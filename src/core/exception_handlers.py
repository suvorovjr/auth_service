from collections.abc import Callable, Coroutine
from http import HTTPStatus
from typing import Any, NoReturn

from fastapi import HTTPException, Request, Response

from src.domain.exceptions import (
    Forbidden,
    OAuthAccessTokenNotFound,
    OAuthResponseDecodeError,
    OAuthTokenExchangeError,
    OAuthUserInfoError,
    PasswordsNotMatch,
    SessionHasExpired,
    UserIsExists,
    UserNotFound,
    WrongEmailOrPassword,
    WrongOldPassword,
)


def create_exception_handler(
    status_code: int, detail: str
) -> Callable[[Request, Exception], Coroutine[Any, Any, NoReturn]]:
    """
    Фабрика для создания обработчиков исключений.

    :param status_code: HTTP-статус, который будет возвращён.
    :param detail: Сообщение об ошибке для клиента.
    :return: Функция-обработчик исключения.
    """

    async def handler(request: Request, exc: Exception) -> NoReturn:
        raise HTTPException(status_code=status_code, detail=detail)

    return handler


user_exists_handler = create_exception_handler(
    status_code=HTTPStatus.BAD_REQUEST,
    detail="Пользователь с таким email уже существует.",
)

passwords_not_match_handler = create_exception_handler(status_code=HTTPStatus.BAD_REQUEST, detail="Пароли не совпадают")

forbidden_handler = create_exception_handler(status_code=HTTPStatus.FORBIDDEN, detail="Доступ запрещен.")

not_authorized_handler = create_exception_handler(
    status_code=HTTPStatus.UNAUTHORIZED, detail="Время жизни сессии истекло."
)

user_not_found_handler = create_exception_handler(status_code=HTTPStatus.NOT_FOUND, detail="Пользователь не найден")

wrong_email_or_password = create_exception_handler(
    status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный email или пароль"
)

wrong_old_password = create_exception_handler(status_code=HTTPStatus.BAD_REQUEST, detail="Неправильный текущий пароль")

oauth_token_exchange_error_handler = create_exception_handler(
    status_code=HTTPStatus.BAD_REQUEST,
    detail="Ошибка при обмене кода на токен от Yandex.",
)

oauth_decode_error_handler = create_exception_handler(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    detail="Ошибка при декодировании ответа от Yandex.",
)

oauth_token_missing_handler = create_exception_handler(
    status_code=HTTPStatus.BAD_REQUEST,
    detail="Отсутствует access token в ответе от Yandex.",
)

oauth_user_info_error_handler = create_exception_handler(
    status_code=HTTPStatus.BAD_GATEWAY,
    detail="Ошибка при получении информации о пользователе от Yandex.",
)


exception_handlers: dict[type[Exception], Callable[[Request, Exception], Coroutine[Any, Any, Response]]] = {
    UserIsExists: user_exists_handler,
    PasswordsNotMatch: passwords_not_match_handler,
    Forbidden: forbidden_handler,
    SessionHasExpired: not_authorized_handler,
    UserNotFound: user_not_found_handler,
    WrongEmailOrPassword: wrong_email_or_password,
    WrongOldPassword: wrong_old_password,
    OAuthTokenExchangeError: oauth_token_exchange_error_handler,
    OAuthResponseDecodeError: oauth_decode_error_handler,
    OAuthAccessTokenNotFound: oauth_token_missing_handler,
    OAuthUserInfoError: oauth_user_info_error_handler,
}
