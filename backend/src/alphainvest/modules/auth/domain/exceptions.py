class AuthError(Exception):
    pass


class InvalidCredentials(AuthError):
    pass


class AccountUnavailable(AuthError):
    pass


class DuplicateEmail(AuthError):
    pass


class InvalidRefreshToken(AuthError):
    pass
