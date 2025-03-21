class UserIsExists(Exception):
    pass


class NotAuthorized(Exception):
    pass


class WrongEmailOrPassword(Exception):
    pass


class WrongOldPassword(Exception):
    pass


class PasswordsNotMatch(Exception):
    pass


class RoleIsExists(Exception):
    pass


class PermissionIsExists(Exception):
    pass


class RoleNotFound(Exception):
    pass


class PermissionNotFound(Exception):
    pass


class UserNotFound(Exception):
    pass


class Forbidden(Exception):
    pass


class SessionHasExpired(Exception):
    pass


class OAuthTokenExchangeError(Exception):
    """Ошибка обмена кода на токен."""

    pass


class OAuthResponseDecodeError(Exception):
    """Ошибка декодирования ответа от OAuth-провайдера."""

    pass


class OAuthAccessTokenNotFound(Exception):
    """Токен не найден в ответе OAuth-провайдера."""

    pass


class OAuthUserInfoError(Exception):
    """Ошибка получения данных пользователя от OAuth-провайдера."""

    pass
