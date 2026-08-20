from src.core.exceptions import AuthenticationError, EntityAlreadyExistsError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    def __init__(self, user_id: object) -> None:
        super().__init__("User", user_id)


class UserAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email {email!r} already exists")


class InvalidCredentialsError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUserError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("This user account has been deactivated")


class InvalidTokenError(AuthenticationError):
    def __init__(self, reason: str = "Invalid or expired token") -> None:
        super().__init__(reason)
