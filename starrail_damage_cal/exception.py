from typing import Union


class UidNotfoundError(Exception):
    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return self.uid


class InvalidUidError(Exception):
    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return self.uid


class CharNameError(Exception):
    def __init__(self, char_name: str):
        self.char_name = char_name

    def __str__(self):
        return self.char_name


class MihomoModelError(Exception):
    def __init__(self, exce: Union[Exception, str]):
        self.exce = exce.args[0] if isinstance(exce, Exception) else exce

    def __str__(self):
        return self.exce


class MihomoQueueTimeoutError(Exception):
    def __str__(self):
        return "Mihomo queue timeout, please try again later."


class MihomoRequestError(Exception):
    def __init__(self, exce: Union[Exception, str]):
        self.exce = exce.args[0] if isinstance(exce, Exception) else exce

    def __str__(self):
        return self.exce


class NotInCharacterShowcaseError(Exception):
    pass


class CharacterShowcaseNotOpenError(Exception):
    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return self.uid
