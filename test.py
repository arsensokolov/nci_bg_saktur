import math

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import pydeck as pdk
# import time
from datetime import datetime, date, timedelta

today = date.today()

st.set_page_config(layout='wide')
st.title('Выпуск путёвок')
st.write('Путёвки автоматически выпускаются на 1 календарный год (12 месяцев) по указанным параметрам.')

st.header('Заездный план выпуска путёвок')
st.subheader('Параметры плана функционирования санатория')

plan_name = st.text_input('Наименование плана', 'План мать и дитя %s' % today.year)

bed_capacity = st.number_input('Коечная мощность', 300)

days_of_stay = st.selectbox('Количество дней пребывания', [14, 18, 21, 29, 30], 0)

arrival_days = st.slider(
    'Количество заездных дней',
    min_value=1,
    max_value=int(days_of_stay),
    value=5,
    step=1,
    help='Количество дней до набора максимальной коечной мощности санатория.'
)

tours_per_day = math.floor(int(bed_capacity) / int(arrival_days))
st.info('Количество путевок в день: %i' % tours_per_day)

period = st.date_input(
    'Период формирования плана',
    (date(today.year, 1, 1), date(today.year, 4, 9)),
    min_value=date(today.year, 1, 1),
    max_value=date(today.year, 12, 31),
    help='Период на которые производится расчет берется из плана функционирования.'
)


st.write('Остановки санатория:')
stops_col1, stops_col2 = st.beta_columns(2)
with stops_col1:
    stops_period = st.date_input(
        'Период',
        (date(today.year, 2, 1), date(today.year, 2, 5)),
        min_value=period[0],
        max_value=period[1]
    )
with stops_col2:
    stops_description = st.text_input('Причина', 'косметический ремонт')


st.write('Сокращение номерного фонда:')
col1, col2, col3 = st.beta_columns(3)
with col1:
    reducing_rooms = st.date_input(
        'Период',
        (date(today.year, 3, 1), date(today.year, 3, 15)),
        min_value=period[0],
        max_value=period[1]
    )
with col2:
    reduce_beds = st.number_input('Количество койкомест', value=10, min_value=0, max_value=int(bed_capacity))
with col3:
    reduce_description = st.text_input('Причина', 'евро ремонт')

reduce_tours_per_day = int(tours_per_day) - math.floor(int(reduce_beds)/int(arrival_days))
st.info('Кол-во путёвок в день при сокращении: %i' % reduce_tours_per_day)

departments = [
    'Отделение "Мать и дитя"',
    'Оздоровительное отделение',
    'Отделение для лечения спинальных больных',
    'Санаторное отделение (с лечением)'
]
department = st.selectbox('Отделение', departments, 1)

days_between_arrival = st.number_input('Количество дней между заездами', value=1, min_value=0)

days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
non_arrivals_days = st.multiselect('Незаездные дни', options=days_of_week, default=['Понедельник', 'Вторник'])

st.header('Ежедневный план выпуска путёвок')
