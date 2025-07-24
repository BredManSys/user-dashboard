import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="User Login Dashboard", layout="wide")
st.title("📊 Дашборд логинов пользователей")

# Загрузка данных
file_path = "data/user_connections.xlsx"

try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"Ошибка чтения файла: {e}")
    st.stop()

# Проверка структуры
required_cols = ["Дата", "Время", "Пользователь", "Айпи"]
if not all(col in df.columns for col in required_cols):
    st.error("Файл должен содержать колонки: Дата, Время, Пользователь, Айпи")
    st.stop()

# Объединение даты и времени
df["Дата"] = pd.to_datetime(df["Дата"].astype(str) + " " + df["Время"].astype(str), format="%Y-%m-%d %H:%M")
df.rename(columns={"Айпи": "IP"}, inplace=True)

# Фильтры (общие)
users = df["Пользователь"].unique()
ips = df["IP"].unique()

st.sidebar.header("🔧 Фильтры")
selected_users = st.sidebar.multiselect("Пользователь", users, default=list(users))
selected_ips = st.sidebar.multiselect("IP-адрес", ips, default=list(ips))

date_min = df["Дата"].min().date()
date_max = df["Дата"].max().date()
date_range = st.sidebar.date_input("Диапазон дат", [date_min, date_max])

search_text = st.sidebar.text_input("Поиск (логин или IP)")

# Фильтрация
filtered = df[
    (df["Дата"].dt.date >= date_range[0]) &
    (df["Дата"].dt.date <= date_range[1]) &
    (df["Пользователь"].isin(selected_users)) &
    (df["IP"].isin(selected_ips))
]

if search_text:
    filtered = filtered[
        filtered["Пользователь"].str.contains(search_text, case=False, na=False) |
        filtered["IP"].str.contains(search_text, na=False)
    ]

# Меню выбора страницы
page = st.sidebar.radio("Раздел", [
    "📈 По дням",
    "🗓️ Календарь активности",
    "⏰ Активность по часам",
    "🏆 ТОП-10 пользователей",
    "🏁 ТОП IP-адресов",
    "👥 Уникальные пользователи по дням",
    "📆 По дням недели"
])

# Разделы дашборда
if page == "📈 По дням":
    st.subheader("📈 Подключения по дням")
    visits = filtered.groupby(filtered["Дата"].dt.date).size().reset_index(name="Подключения")
    fig = px.line(visits, x="Дата", y="Подключения", markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🗓️ Календарь активности":
    st.subheader("🗓️ Календарная плотность активности")
    visits = filtered.groupby(filtered["Дата"].dt.date).size().reset_index(name="Подключения")
    visits["День"] = pd.to_datetime(visits["Дата"]).dt.day
    visits["Месяц"] = pd.to_datetime(visits["Дата"]).dt.month
    fig = px.density_heatmap(
        visits,
        x="День",
        y="Месяц",
        z="Подключения",
        histfunc="sum",
        text_auto=True,
        title="Плотность подключений по календарю"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "⏰ Активность по часам":
    st.subheader("⏰ Активность по часам")
    filtered["Час"] = filtered["Дата"].dt.hour
    hourly = filtered.groupby("Час").size().reset_index(name="Подключения")
    fig = px.bar(hourly, x="Час", y="Подключения", title="Подключения по времени суток")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🏆 ТОП-10 пользователей":
    st.subheader("🏆 Топ-10 самых активных пользователей")
    top_users = filtered["Пользователь"].value_counts().head(10).reset_index()
    top_users.columns = ["Пользователь", "Подключения"]
    fig = px.bar(top_users, x="Пользователь", y="Подключения")
    st.plotly_chart(fig, use_container_width=True)

elif page == "👥 Уникальные пользователи по дням":
    st.subheader("👥 Количество уникальных пользователей в день")
    unique_users = filtered.groupby(filtered["Дата"].dt.date)["Пользователь"].nunique().reset_index()
    unique_users.columns = ["Дата", "Уникальные пользователи"]
    fig = px.line(unique_users, x="Дата", y="Уникальные пользователи")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🏁 ТОП IP-адресов":
    st.subheader("🏁 ТОП IP-адресов по количеству подключений")
    top_ips = filtered["IP"].value_counts().head(10).reset_index()
    top_ips.columns = ["IP-адрес", "Подключения"]
    fig = px.bar(top_ips, x="IP-адрес", y="Подключения", title="Наиболее активные IP-адреса")
    st.plotly_chart(fig, use_container_width=True)

elif page == "📆 По дням недели":
    st.subheader("📆 Активность по дням недели")
    filtered["День недели"] = filtered["Дата"].dt.day_name()
    weekday_counts = filtered["День недели"].value_counts().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ])
    st.bar_chart(weekday_counts)
