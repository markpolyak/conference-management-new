class ValuePasser:
    def __init__(self):
        self._value: int = None

    @property
    def value(self):
        """This is 'value' property."""
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                raise Exception('Can\'t convert specified value string into int')
            value = int(value)
        if value < 1:
            raise Exception('Value must not be less than 1')
        self._value = value
