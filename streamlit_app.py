import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="User Dashboard", layout="wide")
st.title("📊 Дашборд посещений пользователей")

# Загружаем Excel из папки
file_path = "data/user_connections.xlsx"

try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"Не удалось загрузить файл: {e}")
    st.stop()

# Обработка даты
if 'Дата' in df.columns:
    df['Дата'] = pd.to_datetime(df['Дата'])
else:
    st.error("Не найдена колонка с датой")
    st.stop()

# Фильтры
users = df['Пользователь'].unique()
ips = df['IP'].unique()

col1, col2 = st.columns(2)
with col1:
    selected_users = st.multiselect("Пользователь", users, default=users)
with col2:
    selected_ips = st.multiselect("IP", ips, default=ips)

date_min = df['Дата'].min().date()
date_max = df['Дата'].max().date()
date_range = st.date_input("Дата", [date_min, date_max])

# Фильтрация
filtered = df[
    (df['Дата'].dt.date >= date_range[0]) &
    (df['Дата'].dt.date <= date_range[1]) &
    (df['Пользователь'].isin(selected_users)) &
    (df['IP'].isin(selected_ips))
]

# График по дням
visits = filtered.groupby(filtered['Дата'].dt.date).size().reset_index(name="Подключения")
fig = px.line(visits, x='Дата', y='Подключения', markers=True, title="Активность по дням")
st.plotly_chart(fig)

# Календарь
calendar_df = visits.copy()
calendar_df['День'] = pd.to_datetime(calendar_df['Дата']).dt.day
calendar_df['Месяц'] = pd.to_datetime(calendar_df['Дата']).dt.month
fig2 = px.density_heatmap(calendar_df, x="День", y="Месяц", z="Подключения", histfunc="sum", text_auto=True)
st.plotly_chart(fig2)
