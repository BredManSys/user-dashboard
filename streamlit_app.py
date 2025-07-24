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
use
