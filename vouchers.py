import math
from datetime import date
from exceptions import (
    VoucherIntMoreZero,
    VoucherIntBetween,
    VoucherDateRange,
    VoucherDateRangeBetween,
    VoucherTuple,
    VoucherList,
    VoucherRequired,
)

__all__ = ['Voucher']


DateRange = tuple[date, date]


class Voucher(object):
    """Класс Voucher позволяет сформировать заездный план выпуска путёвок.

    Класс реализует алгоритм формирования заездных планов выпуска путёвок
    на основе обязательных и не обязательных атрибутов.

    Attributes
    ----------
    bed_capacity : int
        Коечная мощность. [Обязательный]
    stay_days : int
        Количество дней пребывания (14, 18, 21, 29, 30). [Обязательный]
    arrival_days: int
        Количество заездных дней. [Обязательный]
    period: tuple[date, date]
        Период формирования плана, передаются даты (date) от и по в кортеже (tuple). [Обязательный]
    stop_period: tuple[date, date]
        Период остановки санатория, передаются даты (date) от и по в кортеже (tuple).
        Не может выходить за границы периода формирования плана.
    stops_description: str
        Причина остановки санатория. Указывается как обязательный только
        при указании периода остановки санатория.
    reducing_period: tuple[date, date]
        Период сокращение номерного фонда. Передаются даты (date) от и по в кортеже (tuple).
        Не может выходить за границы периода формирования плана.
    reduce_description: str
        Причина сокращение номерного фонда. Указывается как обязательный только при указании
        периода сокращения номерного фонда.
    days_between_arrival: int
        При необходимости указывается кол-во дней между заездами для проведения профилактических мероприятий.
    non_arrivals_days: list[int]
        При необходимости указываются незаездные дни недели от 1 до нескольких.
        Указывается номер дня недели от 1 до 7, где 1 — понедельник, а 7 — воскресенье.
    """
    CAPTIONS = {
        'bed_capacity':         'bed_capacity (Коечная мощность)',
        'stay_days':            'stay_days (Количество дней пребывания)',
        'arrival_days':         'arrival_days (Количество заездных дней)',
        'period':               'period (Период формирования плана)',
        'stop_period':          'stop_period (Период остановки санатория)',
        'stops_description':    'stops_description (Причина остановки санатория)',
        'reducing_period':      'reducing_period (Период сокращение номерного фонда)',
        'reduce_beds':          'reduce_beds (Количество койкомест)',
        'reduce_description':   'reduce_description (Причина сокращение номерного фонда)',
        'days_between_arrival': 'days_between_arrival (Количество дней между заездами)',
        'non_arrivals_days':    'non_arrivals_days (Незаездные дни)',
    }

    # Защищенные дефолтные значения не обязательных параметров.
    # Для правильной работы не менять!!!
    __stop_period = None
    __stop_description = ''
    __reducing_period = None
    __reduce_beds = 0
    __reduce_description = ''
    __days_between_arrival = 0
    __non_arrivals_days = 0

    def __init__(self, **kwargs):
        # Обязательные параметры
        self.bed_capacity = kwargs.get('bed_capacity', 0)
        self.stay_days = kwargs.get('stay_days', 0)
        self.arrival_days = kwargs.get('arrival_days', 0)
        self.period: DateRange = kwargs.get('period', None)

        # Не обязательные параметры
        self.stop_period = kwargs.get('stop_period', self.__stop_period)
        self.stop_description = kwargs.get('stop_description', self.__stop_description)
        self.reducing_period = kwargs.get('reducing_period', self.__reducing_period)
        self.reduce_beds = kwargs.get('reduce_beds', self.__reduce_beds)
        self.reduce_description = kwargs.get('reduce_description', self.__reduce_description)
        self.days_between_arrival = kwargs.get('days_between_arrival', self.__days_between_arrival)
        self.non_arrivals_days = kwargs.get('non_arrivals_days', self.__non_arrivals_days)

        # Проверим полученные данные
        self.__validate__()

    def __repr__(self):
        date_from, date_to = self.__str_period__()
        return f'{self.__class__.__name__}: Заездный план выпуска путёвок c {date_from} по {date_to} г.г.'

    def __str__(self):
        date_from, date_to = self.__str_period__()
        return f'Заездный план выпуска путёвок c {date_from} по {date_to} г.г.'

    def __str_period__(self):
        """Функция преобразует даты периода формирования плана выпуска путёвок в удобочитаемый формат: ДД-ММ-ГГГГ."""
        date_from, date_to = self.period
        date_from = date_from.strftime('%d.%m.%Y')
        date_to = date_to.strftime('%d.%m.%Y')
        return date_from, date_to

    def __validate__(self):
        """Приватная функция валидации полученных данных при инициализации класса."""

        # Проверим указанную коечную мощность
        if not (self.bed_capacity and isinstance(self.bed_capacity, int) and self.bed_capacity > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['bed_capacity'])

        # Проверим указанное кол-во дней пребывания по 1 путёвке
        if not (self.stay_days and isinstance(self.stay_days, int) and self.stay_days > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['stay_days'])

        # Проверим указанное кол-во заездных дней
        if not (self.arrival_days and isinstance(self.arrival_days, int) and self.stay_days >= self.arrival_days > 0):
            raise VoucherIntBetween(
                (self.CAPTIONS['arrival_days'], self.CAPTIONS['stay_days'])
            )

        # Проверим указанный период формирования плана
        if isinstance(self.period, tuple) and len(self.period) == 2:
            if not (isinstance(self.period[0], date) and isinstance(self.period[1], date)):
                raise VoucherDateRange(self.CAPTIONS['period'])
        else:
            raise VoucherTuple(self.CAPTIONS['period'])

        # Проверим не обязательные параметры
        if self.stop_period:
            self.__validate_stop_period(self.stop_period)
        if self.reducing_period:
            self.__validate_reducing_period(self.reducing_period)
        if self.days_between_arrival:
            self.__validate_days_between_arrival(self.days_between_arrival)
        if self.non_arrivals_days:
            self.__validate_non_arrivals_days(self.non_arrivals_days)

    def __get_stop_description(self):
        return self.__stop_description

    def __set_stop_description(self, value: str):
        self.__stop_description = value

    stop_description = property(__get_stop_description, __set_stop_description)

    def __get_stop_period(self):
        return self.__stop_period

    def __set_stop_period(self, value: tuple):
        self.__validate_stop_period(value)
        self.__stop_period = value

    def __validate_stop_period(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            if not (
                    isinstance(value[0], date) and
                    isinstance(value[1], date) and
                    value[0] >= self.period[0] and value[1] <= self.period[1]
            ):
                raise VoucherDateRangeBetween(
                    (self.CAPTIONS['stop_period'], self.CAPTIONS['period'])
                )
        else:
            raise VoucherTuple(self.CAPTIONS['stop_period'])

        if not self.stop_description:
            raise VoucherRequired(self.CAPTIONS['stop_description'])

    stop_period = property(__get_stop_period, __set_stop_period)

    def __get_reduce_beds(self):
        return self.__reduce_beds

    def __set_reduce_beds(self, value: int):
        self.__validate_reduce_beds(value)
        self.__reduce_beds = value

    def __validate_reduce_beds(self, value):
        if not (value and isinstance(value, int) and value > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['reduce_beds'])

    reduce_beds = property(__get_reduce_beds, __set_reduce_beds)

    def __get_reduce_description(self):
        return self.__reduce_description

    def __set_reduce_description(self, value: str):
        self.__reduce_description = value

    reduce_description = property(__get_reduce_description, __set_reduce_description)

    def __get_reducing_period(self):
        return self.__reducing_period

    def __set_reducing_period(self, value: tuple):
        self.__validate_reducing_period(value)
        self.__reducing_period = value

    def __validate_reducing_period(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            if not (
                    isinstance(value[0], date) and
                    isinstance(value[1], date) and
                    value[0] >= self.period[0] and value[1] <= self.period[1]
            ):
                raise VoucherDateRangeBetween(
                    (self.CAPTIONS['reducing_period'], self.CAPTIONS['period'])
                )
        else:
            raise VoucherTuple(self.CAPTIONS['reducing_period'])

        if not self.reduce_beds:
            raise VoucherRequired(self.CAPTIONS['reduce_beds'])

        if not self.reduce_description:
            raise VoucherRequired(self.CAPTIONS['reduce_description'])

    reducing_period = property(__get_reducing_period, __set_reducing_period)

    def __get_days_between_arrival(self):
        return self.__days_between_arrival

    def __set_days_between_arrival(self, value: int):
        self.__validate_days_between_arrival(value)
        self.__days_between_arrival = value

    def __validate_days_between_arrival(self, value):
        if not isinstance(value, int) and value < 0:
            raise VoucherIntMoreZero(
                self.CAPTIONS['days_between_arrival'],
                'Парамер %s должен быть целочисленным значением больше или равно 0.'
            )

    days_between_arrival = property(__get_days_between_arrival, __set_days_between_arrival)

    def __get_non_arrivals_days(self):
        return self.__non_arrivals_days

    def __set_non_arrivals_days(self, value: list):
        self.__validate_non_arrivals_days(value)
        self.__non_arrivals_days = value

    def __validate_non_arrivals_days(self, value):
        if isinstance(self.non_arrivals_days, list):
            if not all(0 < x < 8 for x in self.non_arrivals_days):
                raise VoucherIntMoreZero(
                    self.CAPTIONS['non_arrivals_days'],
                    'Парамер %s должен быть целочисленным значением от 1 до 7 включительно.'
                )
        else:
            raise VoucherList(self.CAPTIONS['non_arrivals_days'])

    non_arrivals_days = property(__get_non_arrivals_days, __set_non_arrivals_days)

    @property
    def tours_per_day(self):
        return math.floor(self.bed_capacity / self.arrival_days)

    @property
    def reduce_tours_per_day(self):
        return self.tours_per_day - math.floor(self.reduce_beds/self.arrival_days)
