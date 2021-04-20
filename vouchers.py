import math
import pandas as pd
import locale
from datetime import date, timedelta
from exceptions import (
    VoucherIntMoreZero,
    VoucherIntBetween,
    VoucherDateRange,
    VoucherDateRangeBetween,
    VoucherTuple,
    VoucherList,
    VoucherRequired,
)
from typing import Tuple, NoReturn

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
        'bed_capacity': 'bed_capacity (Коечная мощность)',
        'stay_days': 'stay_days (Количество дней пребывания)',
        'arrival_days': 'arrival_days (Количество заездных дней)',
        'period': 'period (Период формирования плана)',
        'stop_period': 'stop_period (Период остановки санатория)',
        'stop_description': 'stop_description (Причина остановки санатория)',
        'reducing_period': 'reducing_period (Период сокращение номерного фонда)',
        'reduce_beds': 'reduce_beds (Количество койкомест)',
        'reduce_description': 'reduce_description (Причина сокращение номерного фонда)',
        'days_between_arrival': 'days_between_arrival (Количество дней между заездами)',
        'non_arrivals_days': 'non_arrivals_days (Незаездные дни)',
    }

    # Защищенные дефолтные значения не обязательных параметров.
    # Для правильной работы не менять!!!
    __stop_period = None
    __stop_description = ''
    __reducing_period = None
    __reduce_beds = 0
    __reduce_description = ''
    __days_between_arrival = 0
    __non_arrivals_days = []

    __stay_days_color = '#ffff00'
    __arrival_days_color = '#00bfff'
    __days_between_arrival_color = '#800080'
    __non_arrivals_days_color = '#808080'

    def __init__(self, **kwargs) -> NoReturn:
        # Обязательные параметры
        self.bed_capacity: int = kwargs.get('bed_capacity', 0)
        self.stay_days: int = kwargs.get('stay_days', 0)
        self.arrival_days: int = kwargs.get('arrival_days', 0)
        self.period: Tuple[date, date] = kwargs.get('period', None)

        # Не обязательные параметры
        self.stop_period: Tuple[date, date] = kwargs.get('stop_period', self.__stop_period)
        self.stop_description: str = kwargs.get('stop_description', self.__stop_description)
        self.reducing_period: Tuple[date, date] = kwargs.get('reducing_period', self.__reducing_period)
        self.reduce_beds: int = kwargs.get('reduce_beds', self.__reduce_beds)
        self.reduce_description: str = kwargs.get('reduce_description', self.__reduce_description)
        self.days_between_arrival: int = kwargs.get('days_between_arrival', self.__days_between_arrival)
        self.non_arrivals_days: list = kwargs.get('non_arrivals_days', self.__non_arrivals_days)

        # Цвета для раскрашивания ячеек данных
        self.stay_days_color: str = kwargs.get('stay_days_color', self.__stay_days_color)
        self.arrival_days_color: str = kwargs.get('arrival_days_color', self.__arrival_days_color)
        self.days_between_arrival_color: str = kwargs.get('days_between_arrival_color',
                                                          self.__days_between_arrival_color)
        self.non_arrivals_days_color: str = kwargs.get('non_arrivals_days_color', self.__non_arrivals_days_color)

        # Проверим полученные данные
        self.__validate__()

        # self.__set_locale__()

    def __repr__(self) -> str:
        date_from, date_to = self.__str_period__()
        return f'{self.__class__.__name__}: Заездный план выпуска путёвок c {date_from} по {date_to} г.г.'

    def __str__(self) -> str:
        date_from, date_to = self.__str_period__()
        return f'Заездный план выпуска путёвок c {date_from} по {date_to} г.г.'

    def __str_period__(self) -> Tuple[str, str]:
        """Функция преобразует даты периода формирования плана выпуска путёвок в удобочитаемый формат: ДД-ММ-ГГГГ."""
        date_from, date_to = self.period
        date_from = date_from.strftime('%d.%m.%Y')
        date_to = date_to.strftime('%d.%m.%Y')
        return date_from, date_to

    @staticmethod
    def __set_locale__() -> NoReturn:
        """Устанавливаем русскую локаль"""
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

    def __validate__(self) -> NoReturn:
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

    @property
    def stop_description(self) -> str:
        return self.__stop_description

    @stop_description.setter
    def stop_description(self, value: str) -> NoReturn:
        self.__stop_description = value

    @property
    def stop_period(self) -> Tuple[date, date]:
        return self.__stop_period

    @stop_period.setter
    def stop_period(self, value: tuple) -> NoReturn:
        if value:
            self.__validate_stop_period(value)
        self.__stop_period = value

    def __validate_stop_period(self, value) -> NoReturn:
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

    @property
    def reduce_beds(self) -> int:
        return self.__reduce_beds

    @reduce_beds.setter
    def reduce_beds(self, value: int) -> NoReturn:
        if value:
            self.__validate_reduce_beds(value)
        self.__reduce_beds = value

    def __validate_reduce_beds(self, value) -> NoReturn:
        if not (value and isinstance(value, int) and value > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['reduce_beds'])

    @property
    def reduce_description(self) -> str:
        return self.__reduce_description

    @reduce_description.setter
    def reduce_description(self, value: str) -> NoReturn:
        self.__reduce_description = value

    @property
    def reducing_period(self) -> Tuple[date, date]:
        return self.__reducing_period

    @reducing_period.setter
    def reducing_period(self, value: tuple) -> NoReturn:
        if value:
            self.__validate_reducing_period(value)
        self.__reducing_period = value

    def __validate_reducing_period(self, value) -> NoReturn:
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

    @property
    def days_between_arrival(self) -> int:
        return self.__days_between_arrival

    @days_between_arrival.setter
    def days_between_arrival(self, value: int) -> NoReturn:
        self.__validate_days_between_arrival(value)
        self.__days_between_arrival = value

    def __validate_days_between_arrival(self, value) -> NoReturn:
        if not isinstance(value, int) and value < 0:
            raise VoucherIntMoreZero(
                self.CAPTIONS['days_between_arrival'],
                'Парамер %s должен быть целочисленным значением больше или равно 0.'
            )

    @property
    def non_arrivals_days(self) -> list:
        return self.__non_arrivals_days

    @non_arrivals_days.setter
    def non_arrivals_days(self, value: list) -> NoReturn:
        self.__validate_non_arrivals_days(value)
        self.__non_arrivals_days = value

    def __validate_non_arrivals_days(self, value) -> NoReturn:
        if isinstance(value, list):
            if not all(0 < x < 8 for x in value):
                raise VoucherIntMoreZero(
                    self.CAPTIONS['non_arrivals_days'],
                    'Парамер %s должен быть целочисленным значением от 1 до 7 включительно.'
                )
        else:
            raise VoucherList(self.CAPTIONS['non_arrivals_days'])

    @property
    def tours_per_day(self) -> int:
        """Кол-во путёвок в день."""
        return math.floor(self.bed_capacity / self.arrival_days)

    @property
    def reduce_tours_per_day(self) -> int:
        """Кол-во путёвок в день при сокращении коечной мощности санатория."""
        return self.tours_per_day - math.floor(self.reduce_beds / self.arrival_days)

    @property
    def dataframe(self) -> pd.DataFrame:
        # даты формирования заездного плана санатория
        date_from, date_to = self.period

        # даты плановой остановки санатория
        stop_date_from, stop_date_to = self.stop_period

        # даты сокращения коечной мощности санатория
        reduce_date_from, reduce_date_to = self.reducing_period

        # подсчитаем длительность периода заездного плана санатория
        period_delta = date_to - date_from

        # список дат заездного плана, для вывода в колонках
        date_list = []

        # строки
        rows = []

        # номер заезда
        arrival_no = 1

        # день заезда
        arrival_day = 1

        # день пребывания
        stay_day = 1

        # необходимое кол-во дней для пропуска.
        # Используется для новых строк.
        skip_days = 0

        # Строка, в виде списка в котором каждый элемент списка является ячейкой для таблицы.
        row = []

        # пробежимся по всему периоду заездного плана
        for day in range(period_delta.days):
            # получим дату для списка
            date_item = date_from + timedelta(days=day)
            # добавим дату в колонку и заодно приведём её к нужному стандарту.
            date_list.append(date_item.strftime('%a, %d %b %y'))

            # проверим дату на нахождения в период остановки санатория
            if stop_date_from <= date_item <= stop_date_to:
                row.append('остановка санатория')
            else:

                if stay_day == 1:
                    row.append('Заезд %i.%i - %i путёвок' % (arrival_no, arrival_day, self.tours_per_day))
                    stay_day += 1
                elif 1 < stay_day < self.stay_days:
                    row.append(self.tours_per_day)
                    stay_day += 1
                elif stay_day == self.stay_days:
                    row.append('выехали %i путёвок' % self.tours_per_day)
                    stay_day += 1
                else:
                    row.append('')
        rows.append(row)

        print(rows)
        df = pd.DataFrame(
            rows,
            columns=date_list
        )
        return df
