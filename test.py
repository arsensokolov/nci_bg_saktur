import base64

import streamlit as st
from datetime import date, timedelta
from vouchers import Voucher

today = date.today()

st.set_page_config(layout='wide', page_title='Тестирование алгоритма выпуска путёвок')
st.title('Выпуск путёвок')

st.sidebar.header('Параметры плана функционирования санатория')

voucher_types = [
    'Заездный',
    'Ежедневный',
]
voucher_type = st.sidebar.radio('Тип плана', voucher_types, 0)

st.header(voucher_type + ' план выпуска путёвок')
voucher_type = voucher_types.index(voucher_type)

sanatorium_name = st.sidebar.text_input('Наименование санатория', 'Маяк')

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

arrival_days = 0
sanitary_days = 0
days_between_arrival = 0

if voucher_type == 0:
    arrival_days = st.sidebar.slider(
        'Количество заездных дней',
        min_value=1,
        max_value=int(days_of_stay),
        value=5,
        step=1,
        help='Количество дней до набора максимальной коечной мощности санатория.'
    )
    sanitary_days = st.sidebar.number_input('Количество санитарных дней', value=3, min_value=0)
elif voucher_type == 1:
    days_between_arrival = st.sidebar.number_input('Количество дней между заездами', value=1, min_value=0)


vouchers = Voucher(
    type=voucher_type,
    sanatorium_name=sanatorium_name,
    department=department,
    bed_capacity=bed_capacity,
    stay_days=days_of_stay,
    period=period,
    non_arrivals_days=non_arrivals_days
)
if voucher_type == 0:
    vouchers.arrival_days = arrival_days
    vouchers.sanitary_days = sanitary_days
elif voucher_type == 1:
    vouchers.days_between_arrival = days_between_arrival

st.sidebar.info('Количество путевок в день: %i' % vouchers.tours_per_day)

stop_sanatorium = st.sidebar.checkbox('Плановая остановка санатория')
if stop_sanatorium:
    stops_period = st.sidebar.date_input(
        'Период',
        value=(date(today.year, 2, 1), date(today.year, 2, 5)),
        min_value=period[0],
        max_value=period[1]
    )
    vouchers.stop_period = stops_period

reduce_sanatorium = st.sidebar.checkbox('Сокращение номерного фонда')
if reduce_sanatorium:
    reducing_period = st.sidebar.date_input(
        'Период',
        (date(today.year, 3, 1), date(today.year, 3, 15)),
        min_value=period[0],
        max_value=period[1]
    )
    reduce_beds = st.sidebar.number_input('Количество койкомест', value=10, min_value=0, max_value=int(bed_capacity))
    vouchers.reduce_beds = reduce_beds
    vouchers.reducing_period = reducing_period

    st.sidebar.info('Кол-во путёвок в день при сокращении: %i' % vouchers.reduce_tours_per_day)

df = vouchers.dataframe
st.dataframe(df)


def get_tabele_dowload_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="vouchers.csv">Сказать таблицу в CSV файле</a>'


st.markdown(get_tabele_dowload_link(df), unsafe_allow_html=True)

# if st.button('Скачать CSV'):
#     df.to_csv('output.csv')

with st.beta_expander('Документация'):
    st.help(vouchers)
