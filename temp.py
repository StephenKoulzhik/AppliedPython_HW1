import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from time import time


# Функция для определения сезона
def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Fall"


# Анализ данных для одного города
def analyze_city(city_data):
    city_data["season"] = city_data["date"].apply(get_season)
    city_data["30d_ma"] = (
        city_data["temperature"].rolling(window=30, min_periods=1).mean()
    )

    # Средние значения и стандартное отклонение по сезонам
    seasonal_stats = (
        city_data.groupby("season")["temperature"].agg(["mean", "std"]).reset_index()
    )
    city_data = city_data.merge(seasonal_stats, on="season", how="left")

    # Вычисление границ аномалий
    city_data["lower_bound"] = city_data["mean"] - 2 * city_data["std"]
    city_data["upper_bound"] = city_data["mean"] + 2 * city_data["std"]
    city_data["is_anomaly"] = (city_data["temperature"] < city_data["lower_bound"]) | (
        city_data["temperature"] > city_data["upper_bound"]
    )
    return city_data


# Основной анализ с распараллеливанием
def analyze_data_parallel(df):
    cities = df["city"].unique()
    city_data_splits = [df[df["city"] == city] for city in cities]
    results = Parallel(n_jobs=-1)(
        delayed(analyze_city)(city_data) for city_data in city_data_splits
    )
    return pd.concat(results)


# Без распараллеливания
def analyze_data_serial(df):
    results = []
    for city in df["city"].unique():
        city_data = df[df["city"] == city]
        results.append(analyze_city(city_data))
    return pd.concat(results)


# Сравнение производительности
def compare_performance(file_path):
    df = pd.read_csv(file_path, parse_dates=["date"])

    # Без распараллеливания
    start_time = time()
    result_serial = analyze_data_serial(df)
    time_serial = time() - start_time

    # С распараллеливанием
    start_time = time()
    result_parallel = analyze_data_parallel(df)
    time_parallel = time() - start_time

    print(f"Время выполнения без распараллеливания: {time_serial:.2f} секунд")
    print(f"Время выполнения с распараллеливанием: {time_parallel:.2f} секунд")


# Пример использования
file_path = "temperature_data.csv"  # Путь к файлу с данными
compare_performance(file_path)
