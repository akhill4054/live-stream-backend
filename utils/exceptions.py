class InvalidRequestError(BaseException):
    def __init__(self, message=None, *args: object) -> None:
        self.message = message
        super().__init__(self.message, *args)
