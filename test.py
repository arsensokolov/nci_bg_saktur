import streamlit as st
from datetime import date, timedelta
from vouchers import Voucher

today = date.today()

st.set_page_config(layout='wide', page_title='Тестирование алгоритма выпуска путёвок')
st.title('Выпуск путёвок')
st.header('Заездный план выпуска путёвок')

st.sidebar.header('Параметры плана функционирования санатория')
sanatorium_name = st.sidebar.text_input('Наименование санатория', 'Маяк')

plan_name = st.sidebar.text_input('Наименование плана', 'План мать и дитя %s' % today.year)

departments = [
    'Отделение "Мать и дитя"',
    'Оздоровительное отделение',
    'Отделение для лечения спинальных больных',
    'Санаторное отделение (с лечением)'
]
department = st.sidebar.selectbox('Отделение', departments, 1)

bed_capacity = st.sidebar.number_input('Коечная мощность', value=300, min_value=1)
period = st.sidebar.date_input(
    'Период формирования плана',
    (date(today.year, 1, 1), date(today.year, 4, 9)),
    min_value=date(today.year, 1, 1),
    max_value=date(today.year, 12, 31),
    help='Период на которые производится расчет берется из плана функционирования.'
)

days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
non_arrivals_days = st.sidebar.multiselect('Незаездные дни', options=days_of_week, default=['Понедельник', 'Вторник'])
non_arrivals_days = [days_of_week.index(x) for x in non_arrivals_days]


days_of_stay = st.sidebar.selectbox('Количество дней пребывания', [14, 18, 21, 29, 30], 0)
arrival_days = st.sidebar.slider(
    'Количество заездных дней',
    min_value=1,
    max_value=int(days_of_stay),
    value=5,
    step=1,
    help='Количество дней до набора максимальной коечной мощности санатория.'
)
days_between_arrival = st.sidebar.number_input('Количество дней между заездами', value=1, min_value=0)

vouchers = Voucher(
    sanatorium_name=sanatorium_name,
    bed_capacity=bed_capacity,
    stay_days=days_of_stay,
    arrival_days=arrival_days,
    period=period,
    days_between_arrival=days_between_arrival,
    non_arrivals_days=non_arrivals_days
)
st.sidebar.info('Количество путевок в день: %i' % vouchers.tours_per_day)

stop_sanatorium = st.sidebar.checkbox('Остановки санатория')
if stop_sanatorium:
    stops_period = st.sidebar.date_input(
        'Период',
        value=(date(today.year, 2, 1), date(today.year, 2, 5)),
        min_value=period[0],
        max_value=period[1]
    )
    stops_description = st.sidebar.text_input('Причина', 'косметический ремонт')
    vouchers.stop_description = stops_description
    vouchers.stop_period = stops_period

# st.sidebar.subheader('Сокращение номерного фонда')
# reducing_period = st.sidebar.date_input(
#     'Период',
#     (date(today.year, 3, 1), date(today.year, 3, 15)),
#     min_value=period[0],
#     max_value=period[1]
# )
# reduce_beds = st.sidebar.number_input('Количество койкомест', value=10, min_value=0, max_value=int(bed_capacity))
# reduce_description = st.sidebar.text_input('Причина', 'евро ремонт')
# vouchers.reduce_beds = reduce_beds
# vouchers.reduce_description = reduce_description
# vouchers.reducing_period = reducing_period
#
# st.sidebar.info('Кол-во путёвок в день при сокращении: %i' % vouchers.reduce_tours_per_day)

st.dataframe(vouchers.dataframe)
with st.beta_expander('Документация'):
    st.help(vouchers)
