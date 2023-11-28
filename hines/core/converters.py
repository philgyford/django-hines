# Used for URL confs.


class FourDigitYearConverter:
    "Matches 4 digits."

    regex = r"[0-9]{4}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{int(value):04d}"


class TwoDigitMonthConverter:
    "Matches 2 digits."

    regex = r"[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{int(value):02d}"


class TwoDigitDayConverter:
    "Matches 2 digits."

    regex = r"[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{int(value):02d}"


class WordCharacterConverter:
    "Matches a string of any 'word' characters; no punctuation."

    regex = r"\w+"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return value
