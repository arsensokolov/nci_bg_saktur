class VoucherIntMoreZero(Exception):
    def __init__(self, parameter: str, message='Парамер %s должен быть целочисленным значением больше 0.'):
        self.message = message % parameter
        super(VoucherIntMoreZero, self).__init__(self.message)


class VoucherIntBetween(Exception):
    def __init__(self, parameters: tuple, message: str = ''):
        self.message = 'Парамер %s должен быть целочисленных значением больше 0 ' \
                       'и меньше параметра %s.' % parameters
        super(VoucherIntBetween, self).__init__(self.message)


class VoucherDateRange(Exception):
    def __init__(self, parameter: str, message='Параметр %s должен быть периодом с датами: tuple(date(), date()).'):
        self.message = message % parameter
        super(VoucherDateRange, self).__init__(self.message)


class VoucherDateRangeBetween(Exception):
    def __init__(self, parameters: tuple, message=(
            'Параметр %s должен быть периодом с датами в промежутке между датами параметра %s: tuple(date(), date())'
    )):
        self.message = message % parameters
        super(VoucherDateRangeBetween, self).__init__(self.message)


class VoucherTuple(Exception):
    def __init__(self, parameter, message='Параметр %s не является кортежем (tuple).'):
        self.message = message % parameter
        super(VoucherTuple, self).__init__(self.message)


class VoucherList(Exception):
    def __init__(self, parameter, message='Параметр %s не является списком (list).'):
        self.message = message % parameter
        super(VoucherList, self).__init__(self.message)


class VoucherRequired(Exception):
    def __init__(self, parameter, message='Параметр %s является обязательным.'):
        self.message = message % parameter
        super(VoucherRequired, self).__init__(self.message)
