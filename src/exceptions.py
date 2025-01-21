class ExceptionWithMessageForUser(Exception):
    message: str = None
    message_for_user: str = 'An unexpected error occurred'

    def __init__(self, message=None, message_for_user=None):
        super().__init__(self.message or message)
        self.message_for_user = self.message_for_user or message_for_user

    def __str__(self):
        return f"{super().__str__()}\n(User Message: {self.message_for_user})"
