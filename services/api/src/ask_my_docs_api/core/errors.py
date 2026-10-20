class AppError(Exception):
    code = "internal"
    default_message = "Internal Error"

    def __init__(self, message: str | None = None) -> None:
        text = message if message is not None else self.default_message
        self.message = text
        super().__init__(text)


class NotFoundError(AppError):
    code = "not_found"
    default_message = "Not found"


class BadRequestError(AppError):
    code = "bad_request"
    default_message = "Bad request Error"


class ConflictError(AppError):
    code = "conflict"
    default_message = "Conflict Error"


class UnauthorizedError(AppError):
    code = "unauthorized"
    default_message = "Invalid or missing API key"
