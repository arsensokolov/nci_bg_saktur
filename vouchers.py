import datetimerange as dtr
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
from typing import Tuple, NoReturn, Union

__all__ = ['Voucher']

DateRange = tuple[date, date]


class Voucher(object):
    """Класс Voucher позволяет сформировать заездный план выпуска путёвок.

    Класс реализует алгоритм формирования заездных планов выпуска путёвок
    на основе обязательных и не обязательных атрибутов.

    Атрибуты
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
    reducing_period: tuple[date, date]
        Период сокращение номерного фонда. Передаются даты (date) от и по в кортеже (tuple).
        Не может выходить за границы периода формирования плана.
        При необходимости указывается кол-во дней между заездами для проведения профилактических мероприятий.
    reduce_beds: int
        Указывается кол-во коек которые будет убрано из эксплуатации на период сокращения номерного фонда.
        Не может быть больше коечной мощности санатория.
    non_arrivals_days: list[int]
        При необходимости указываются незаездные дни недели от 1 до нескольких.
        Указывается номер дня недели от 1 до 7, где 1 — понедельник, а 7 — воскресенье.

    dataframe:
        Атрибут возвращает датафрейм для формирования таблицы данных. Только для чтения.
    """
    CAPTIONS = {
        'type': 'type (Тип плана)',
        'bed_capacity': 'bed_capacity (Коечная мощность)',
        'stay_days': 'stay_days (Количество дней пребывания)',
        'arrival_days': 'arrival_days (Количество заездных дней)',
        'period': 'period (Период формирования плана)',
        'stop_period': 'stop_period (Период остановки санатория)',
        'stop_description': 'stop_description (Причина остановки санатория)',
        'reducing_period': 'reducing_period (Период сокращение номерного фонда)',
        'reduce_beds': 'reduce_beds (Количество койкомест)',
        'reduce_description': 'reduce_description (Причина сокращение номерного фонда)',
        'sanitary_days': 'sanitary_days (Количество санитарных дней)',
        'days_between_arrival': 'days_between_arrival (Количество дней между заездами)',
        'non_arrivals_days': 'non_arrivals_days (Незаездные дни)',
    }

    # Защищенные дефолтные значения не обязательных параметров.
    # Для правильной работы не менять!!!
    __arrival_days = 0
    __stop_period = None
    __stop_description = ''
    __reducing_period = None
    __reduce_beds = 0
    __reduce_description = ''
    __days_between_arrival = 0
    __sanitary_days = 0
    __non_arrivals_days = []

    def __init__(self, **kwargs) -> NoReturn:
        # Обязательные параметры
        self.type: int = kwargs.get('type', 0)
        self.bed_capacity: int = kwargs.get('bed_capacity', 0)
        self.stay_days: int = kwargs.get('stay_days', 0)
        self.period: Tuple[date, date] = kwargs.get('period', None)
        self.sanatorium_name: str = kwargs.get('sanatorium_name', '')
        self.department: str = kwargs.get('department', '')

        # Не обязательные параметры
        self.arrival_days: int = kwargs.get('arrival_days', self.__arrival_days)
        self.stop_period: Tuple[date, date] = kwargs.get('stop_period', self.__stop_period)
        self.stop_description: str = kwargs.get('stop_description', self.__stop_description)
        self.reducing_period: Tuple[date, date] = kwargs.get('reducing_period', self.__reducing_period)
        self.reduce_beds: int = kwargs.get('reduce_beds', self.__reduce_beds)
        self.reduce_description: str = kwargs.get('reduce_description', self.__reduce_description)
        self.sanitary_days: int = kwargs.get('sanitary_days', self.__sanitary_days)
        self.days_between_arrival: int = kwargs.get('days_between_arrival', self.__days_between_arrival)
        self.non_arrivals_days: list = kwargs.get('non_arrivals_days', self.__non_arrivals_days)

        # Проверим полученные данные
        self.__validate__()

        self.__set_locale__()

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
        """Пытаемся установить русскую локаль"""
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            pass

    def __validate__(self) -> NoReturn:
        """Приватная функция валидации полученных данных при инициализации класса."""

        # Проверим чтобы тип плана передавался конкретным целочисленным значением
        if not isinstance(self.type, int) and 0 > self.type > 1:
            raise VoucherRequired(self.CAPTIONS['type'])

        # Проверим указанную коечную мощность
        if not (self.bed_capacity and isinstance(self.bed_capacity, int) and self.bed_capacity > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['bed_capacity'])

        # Проверим указанное кол-во дней пребывания по 1 путёвке
        if not (self.stay_days and isinstance(self.stay_days, int) and self.stay_days > 0):
            raise VoucherIntMoreZero(self.CAPTIONS['stay_days'])

        # Проверим указанный период формирования плана
        if isinstance(self.period, tuple) and len(self.period) == 2:
            if not (isinstance(self.period[0], date) and isinstance(self.period[1], date)):
                raise VoucherDateRange(self.CAPTIONS['period'])
        else:
            raise VoucherTuple(self.CAPTIONS['period'])

        # Проверим не обязательные параметры
        if self.arrival_days:
            self.__validate_arrival_days(self.arrival_days)
        if self.stop_period:
            self.__validate_stop_period(self.stop_period)
        if self.reducing_period:
            self.__validate_reducing_period(self.reducing_period)
        if self.sanitary_days:
            self.__validate_sanitary_days(self.sanitary_days)
        if self.days_between_arrival:
            self.__validate_days_between_arrival(self.days_between_arrival)
        if self.non_arrivals_days:
            self.__validate_non_arrivals_days(self.non_arrivals_days)

    @property
    def arrival_days(self) -> int:
        return self.__arrival_days

    @arrival_days.setter
    def arrival_days(self, value: int) -> NoReturn:
        if value:
            self.__validate_arrival_days(value)
        self.__arrival_days = value

    def __validate_arrival_days(self, value) -> NoReturn:
        """Валидатор проверяет указанное кол-во заездных дней."""
        if not (isinstance(value, int) and self.stay_days >= value > 0):
            raise VoucherIntBetween(
                (self.CAPTIONS['arrival_days'], self.CAPTIONS['stay_days'])
            )

    @property
    def stop_description(self) -> str:
        return self.__stop_description

    @stop_description.setter
    def stop_description(self, value: str) -> NoReturn:
        self.__stop_description = value

    @property
    def stop_period(self) -> tuple[date, date]:
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

        # if not self.stop_description:
        #     raise VoucherRequired(self.CAPTIONS['stop_description'])

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

        # if not self.reduce_description:
        #     raise VoucherRequired(self.CAPTIONS['reduce_description'])

    @property
    def sanitary_days(self) -> int:
        return self.__sanitary_days

    @sanitary_days.setter
    def sanitary_days(self, value: int) -> NoReturn:
        self.__validate_sanitary_days(value)
        self.__sanitary_days = value

    def __validate_sanitary_days(self, value) -> NoReturn:
        if not isinstance(value, int) and value < 0:
            raise VoucherIntMoreZero(
                self.CAPTIONS['sanitary_days'],
                'Параметр %s должен быть целочисленным значением больше или равно 0.'
            )

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
            if not all(0 <= x <= 7 for x in value):
                raise VoucherIntMoreZero(
                    self.CAPTIONS['non_arrivals_days'],
                    'Парамер %s должен быть целочисленным значением от 0 до 6 включительно.'
                )
            if len(value) >= 7:
                raise Exception('Нельзя указывать все дни недели.')
        else:
            raise VoucherList(self.CAPTIONS['non_arrivals_days'])

    @property
    def tours_per_day(self) -> int:
        """Кол-во путёвок в день."""
        if self.type == 0:
            return math.floor(self.bed_capacity / self.arrival_days)
        elif self.type == 1:
            return math.floor(self.bed_capacity / self.stay_days)

    @property
    def reduce_tours_per_day(self) -> int:
        """Кол-во путёвок в день при сокращении коечной мощности санатория."""
        return self.tours_per_day - math.floor(self.reduce_beds / self.arrival_days)

    @property
    def dataframe(self) -> pd.DataFrame:
        rows = []
        data = []
        while True:
            data = self.get_arrival(data)
            if not data:
                break
            for row in data:
                if self.type == 1:
                    rows.append([
                        self.sanatorium_name,
                        self.department,
                        row[0],
                        row[2].strftime('%d.%m.%y - %a'),
                        self.stay_days,
                        row[3].strftime('%d.%m.%y'),
                        row[4],
                        '%i/%i' % (row[5], row[6]),
                        self.days_between_arrival
                    ])
                else:
                    rows.append([
                        self.sanatorium_name,
                        self.department,
                        row[0],
                        row[1],
                        row[2].strftime('%d.%m.%y - %a'),
                        self.stay_days,
                        row[3].strftime('%d.%m.%y'),
                        row[4],
                        row[8],
                        row[9],
                        '%i/%i' % (row[5], row[6]),
                        row[7],
                    ])

        if self.type == 1:
            columns = [
                'Здравница',
                'Отделение',
                'Заезд',
                'Начало заезда',
                'Кол-во дней',
                'Окончание заезда',
                'Кол-во путёвок',
                'Заполненность санатория',
                'Между заездом дн.',
            ]
        else:
            columns = [
                'Здравница',
                'Отделение',
                'Заезд',
                'День заезда',
                'Начало заезда',
                'Кол-во дней',
                'Окончание заезда',
                'Кол-во путёвок',
                '№ путёвок с',
                '№ путёвок по',
                'Заполненность санатория',
                'Санитарных дн.',
            ]

        df = pd.DataFrame(
            rows,
            columns=columns
        )
        return df

    def get_arrival(self, prev_arrival: Union[list, None] = None) -> list:
        data = []
        # rest_beds = prev_arrival[-1][5] if prev_arrival else 0
        rest_beds = 0
        arrival_number = prev_arrival[-1][0] + 1 if prev_arrival else 1
        sanitary_days = self.sanitary_days
        arrival_day = 0
        day_iterate = 0
        start_date, end_date = self.period
        voucher_number_from = 1

        # дни/период остановки санатория
        stop_period = []
        if self.stop_period:
            stop_period = dtr.DateTimeRange(*self.stop_period)

        # дни/период ограничения санатория
        reducing_period = []
        if self.reducing_period:
            reducing_period = dtr.DateTimeRange(*self.reducing_period)

        prev_arrival_end_dates = []
        if prev_arrival:
            # start_date = prev_arrival[arrival_day][3]
            start_date = prev_arrival[-1][3] + timedelta(days=prev_arrival[-1][7] + 1)
            voucher_number_from = prev_arrival[-1][9] + 1
            # prev_arrival_end_dates = [x[3] for x in prev_arrival]
            # настроим все необходимые параметры если была остановка санатория
            # и предыдущий заезд полностью не завершился
            if stop_period and start_date < stop_period.end_datetime.date() and len(prev_arrival) < self.arrival_days:
                start_date = stop_period.end_datetime.date() + timedelta(days=1)
                rest_beds = 0
                prev_arrival = []

        good_day = True
        bed_capacity = self.bed_capacity
        tours_per_day = self.tours_per_day
        voucher_number_to = voucher_number_from + tours_per_day

        while arrival_day < self.arrival_days:
            # начальная дата — заселение
            arrival_start_date = start_date + timedelta(days=day_iterate)
            # конечная дата — выселение
            arrival_end_date = arrival_start_date + timedelta(days=self.stay_days - 1)
            # период заселения
            arrival_period = dtr.DateTimeRange(arrival_start_date, arrival_end_date)

            if stop_period and arrival_period.is_intersection(stop_period):
                break

            if prev_arrival:
                try:
                    if arrival_start_date in prev_arrival_end_dates:
                        # вычитаем съехавших из санатория
                        rest_beds -= prev_arrival[arrival_day][4]
                except IndexError:
                    pass

                # try:
                #     # создаём профилактический день
                #     preventive_day = prev_arrival[arrival_day][3] + timedelta(days=self.days_between_arrival + 1)
                #     # если профилактический день всё ещё больше даты начала заезда:
                #     if preventive_day > arrival_start_date:
                #         # помечаем день плохим, т.к. в него ещё нельзя заезжать.
                #         good_day = False
                #     else:
                #         good_day = True
                # except IndexError:
                #     pass

            # если дата выселения выходит за границы конца заездного плана прерываем цикл
            if arrival_end_date > end_date:
                break

            # установим коечную мощность и кол-во путёвок в день для заселения,
            # если период заселения пересекается в периодом ограниченного функционирования санатория
            if reducing_period and arrival_period.is_intersection(reducing_period):
                tours_per_day = self.reduce_tours_per_day
                bed_capacity = self.bed_capacity - self.reduce_beds
                voucher_number_to = voucher_number_from + tours_per_day

            # проверяем чтобы заезд был не в запрещённые дни недели
            if (arrival_start_date.weekday() not in self.non_arrivals_days and
                    good_day and
                    rest_beds + tours_per_day <= bed_capacity):
                # добавим поселенцев в санаторий
                rest_beds = rest_beds + tours_per_day

                # пересчитаем новые номера путёвок с учётом прошедшего заселения
                if arrival_day > 0:
                    voucher_number_from = voucher_number_from + tours_per_day + 1
                    voucher_number_to = voucher_number_from + tours_per_day

                # добьём кол-во путёвок по остаточным свободным местам
                if arrival_day + 1 == self.arrival_days and rest_beds < bed_capacity:
                    odd = bed_capacity - rest_beds
                    tours_per_day += odd
                    rest_beds += odd

                skip_days_after = 0
                if arrival_day + 1 == self.arrival_days:
                    skip_days_after = self.sanitary_days

                # сформируем массив данных
                data.append([
                    arrival_number,
                    arrival_day + 1,
                    arrival_start_date,
                    arrival_end_date,
                    tours_per_day,
                    rest_beds,
                    bed_capacity,
                    skip_days_after,
                    voucher_number_from,
                    voucher_number_to,
                ])
                arrival_day += 1
            day_iterate += 1
        return data
