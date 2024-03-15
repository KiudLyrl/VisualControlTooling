# -*- coding: utf-8 -*

class RecoverableException(Exception):
    """
    Throw this if you think the bot coder could find a way around the error
    """
    def __init__(self, message):
        self.message = message


class UnrecoverableException(Exception):
    def __init__(self, message):
        self.message = message
