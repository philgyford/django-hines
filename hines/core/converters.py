# Used for URL confs.


class FourDigitYearConverter:
    "Matches 4 digits."
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '{:04d}'.format(int(value))


class TwoDigitMonthConverter:
    "Matches 2 digits."
    regex = '[0-9]{2}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '{:02d}'.format(int(value))


class TwoDigitDayConverter:
    "Matches 2 digits."
    regex = '[0-9]{2}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '{:02d}'.format(int(value))


class WordCharacterConverter:
    "Matches a string of any 'word' characters; no punctuation."
    regex = '\w+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return value

