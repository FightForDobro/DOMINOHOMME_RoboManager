class BotError(Exception):
    pass

class FatalException(BotError):
    pass

class UserDoesNotExists(BotError):
    pass

