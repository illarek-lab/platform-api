class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidGoogleTokenError(AuthError):
    pass
