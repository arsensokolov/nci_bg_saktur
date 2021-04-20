import math

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import pydeck as pdk
# import time
from datetime import datetime, date, timedelta
from vouchers import Voucher

today = date.today()

st.set_page_config(layout='wide')
st.title('Выпуск путёвок')
st.write('Путёвки автоматически выпускаются на 1 календарный год (12 месяцев) по указанным параметрам.')

st.header('Заездный план выпуска путёвок')
st.subheader('Параметры плана функционирования санатория')

plan_name = st.text_input('Наименование плана', 'План мать и дитя %s' % today.year)

bed_capacity = st.number_input('Коечная мощность', 300)

# ds_col1, ds_col2 = st.beta_columns(2)
# with ds_col1:
days_of_stay = st.selectbox('Количество дней пребывания', [14, 18, 21, 29, 30], 0)
# with ds_col2:
#     days_of_stay_color = st.color_picker('Цвет дня пребывания', '#ffff00')

# ad_col1, ad_col2 = st.beta_columns(2)
# with ad_col1:
arrival_days = st.slider(
    'Количество заездных дней',
    min_value=1,
    max_value=int(days_of_stay),
    value=5,
    step=1,
    help='Количество дней до набора максимальной коечной мощности санатория.'
)
# with ad_col2:
#     arrival_days_color = st.color_picker('Цвет начала периода заезда', '#00bfff')

period = st.date_input(
    'Период формирования плана',
    (date(today.year, 1, 1), date(today.year, 4, 9)),
    min_value=date(today.year, 1, 1),
    max_value=date(today.year, 12, 31),
    help='Период на которые производится расчет берется из плана функционирования.'
)
vouchers = Voucher(bed_capacity=bed_capacity, stay_days=days_of_stay, arrival_days=arrival_days, period=period)
st.info('Количество путевок в день: %i' % vouchers.tours_per_day)


st.write('Остановки санатория:')
stops_col1, stops_col2 = st.beta_columns(2)
# stops_col1, stops_col2, stops_col3 = st.beta_columns(3)
with stops_col1:
    stops_period = st.date_input(
        'Период',
        (date(today.year, 2, 1), date(today.year, 2, 5)),
        min_value=period[0],
        max_value=period[1]
    )
with stops_col2:
    stops_description = st.text_input('Причина', 'косметический ремонт')
# with stops_col3:
#     stops_color = st.color_picker('Цвет остановки санатория', '#ff0000')
vouchers.stop_description = stops_description
vouchers.stop_period = stops_period


st.write('Сокращение номерного фонда:')
# col1, col2, col3, col4 = st.beta_columns(4)
col1, col2, col3 = st.beta_columns(3)
with col1:
    reducing_period = st.date_input(
        'Период',
        (date(today.year, 3, 1), date(today.year, 3, 15)),
        min_value=period[0],
        max_value=period[1]
    )
with col2:
    reduce_beds = st.number_input('Количество койкомест', value=10, min_value=0, max_value=int(bed_capacity))
with col3:
    reduce_description = st.text_input('Причина', 'евро ремонт')
# with col4:
#     reduce_color = st.color_picker('Цвет сокращения номерного фонда', '#ffa500')
vouchers.reduce_beds = reduce_beds
vouchers.reduce_description = reduce_description
vouchers.reducing_period = reducing_period

vouchers.reduce_beds = reduce_beds
vouchers.reduce_description = reduce_description
vouchers.reducing_period = reducing_period
st.info('Кол-во путёвок в день при сокращении: %i' % vouchers.reduce_tours_per_day)

departments = [
    'Отделение "Мать и дитя"',
    'Оздоровительное отделение',
    'Отделение для лечения спинальных больных',
    'Санаторное отделение (с лечением)'
]
department = st.selectbox('Отделение', departments, 1)

# dba_col1, dba_col2 = st.beta_columns(2)
# with dba_col1:
days_between_arrival = st.number_input('Количество дней между заездами', value=1, min_value=0)
vouchers.days_between_arrival = days_between_arrival
# with dba_col2:
#     days_between_arrival_color = st.color_picker('Цвет дня между заездами', '#800080')

# wd_col1, wd_col2 = st.beta_columns(2)
# with wd_col1:
days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
non_arrivals_days = st.multiselect('Незаездные дни', options=days_of_week, default=['Понедельник', 'Вторник'])
non_arrivals_days = [days_of_week.index(x) + 1 for x in non_arrivals_days]
vouchers.non_arrivals_days = non_arrivals_days
# nad = [days_of_week[x - 1] for x in non_arrivals_days]
# st.write(nad)
# with wd_col2:
#     non_arrivals_days_color = st.color_picker('Цвет незаездных дней', '#808080')

st.subheader('Результат расчёта плана заезда')
st.dataframe(vouchers.dataframe)

st.header('Ежедневный план выпуска путёвок')
