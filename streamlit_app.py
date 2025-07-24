import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="User Login Dashboard", layout="wide")
st.title("📊 Дашборд логинов пользователей")

# Путь к Excel-файлу
file_path = "data/user_connections.xlsx"

try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"Ошибка чтения файла: {e}")
    st.stop()

# Проверка наличия нужных колонок
required_cols = ["Дата", "Время", "Пользователь", "Айпи"]
if not all(col in df.columns for col in required_cols):
    st.error("Файл должен содержать колонки: Дата, Время, Пользователь, Айпи")
    st.stop()

# Объединяем дату и время в одну колонку datetime
df["Дата"] = pd.to_datetime(df["Дата"].astype(str) + " " + df["Время"].astype(str), format="%Y-%m-%d %H:%M")

# Переименовываем 'Айпи' → 'IP' для удобства
df.rename(columns={"Айпи": "IP"}, inplace=True)

# Фильтры
users = df["Пользователь"].unique()
ips = df["IP"].unique()

col1, col2 = st.columns(2)
with col1:
    selected_users = st.multiselect("Пользователь", users, default=list(users))
with col2:
    selected_ips = st.multiselect("IP-адрес", ips, default=list(ips))

date_min = df["Дата"].min().date()
date_max = df["Дата"].max().date()
date_range = st.date_input("Выберите диапазон дат", [date_min, date_max])

# Фильтрация
filtered = df[
    (df["Дата"].dt.date >= date_range[0]) &
    (df["Дата"].dt.date <= date_range[1]) &
    (df["Пользователь"].isin(selected_users)) &
    (df["IP"].isin(selected_ips))
]

# 📈 График подключений по дням
visits = filtered.groupby(filtered["Дата"].dt.date).size().reset_index(name="Подключения")
st.subheader("📈 Подключения по дням")
fig = px.line(visits, x="Дата", y="Подключения", markers=True)
st.plotly_chart(fig, use_container_width=True)

# 🗓️ Календарь активности
st.subheader("🗓️ Календарная плотность активности")
calendar_df = visits.copy()
calendar_df["День"] = pd.to_datetime(calendar_df["Дата"]).dt.day
calendar_df["Месяц"] = pd.to_datetime(calendar_df["Дата"]).dt.month
fig2 = px.density_heatmap(
    calendar_df,
    x="День",
    y="Месяц",
    z="Подключения",
    histfunc="sum",
    text_auto=True,
    title="Плотность подключений по календарю"
)
st.plotly_chart(fig2, use_container_width=True)
