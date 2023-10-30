class UidNotfoundError(Exception):
    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return repr(self.uid)


class CharNameError(Exception):
    def __init__(self, char_name: str):
        self.char_name = char_name

    def __str__(self):
        return repr(self.char_name)


class MihomoRequestError(Exception):
    pass


class NotInCharacterShowcaseError(Exception):
    pass


class CharacterShowcaseNotOpenError(Exception):
    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return repr(self.uid)
