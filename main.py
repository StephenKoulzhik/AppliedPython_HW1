import streamlit as st
from PIL import Image
import datetime
import asyncio
import aiohttp
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import serpapi


URL_TEMPLATE = "https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"


def date_to_season(date):
    if date.month in [12, 1, 2]:
        return "winter"
    elif date.month in [3, 4, 5]:
        return "spring"
    elif date.month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


def analyze_city(city_data):
    city_data["rolling_mean"] = (
        city_data["temperature"].rolling(window=30, min_periods=1).mean()
    )

    seasonal_stats = (
        city_data.groupby("season")["temperature"].agg(["mean", "std"]).reset_index()
    )
    city_data = city_data.merge(seasonal_stats, on="season", how="left")

    city_data["lower_bound"] = city_data["mean"] - 2 * city_data["std"]
    city_data["upper_bound"] = city_data["mean"] + 2 * city_data["std"]
    city_data["is_anomaly"] = ((city_data["temperature"] < city_data["lower_bound"]) | (city_data["temperature"] > city_data["upper_bound"])).astype(int)

    return city_data


def analyze_data_full(df):
    results = []
    for city in df["city"].unique():
        city_data = df[df["city"] == city]
        results.append(analyze_city(city_data))
    return pd.concat(results)


def preprocessing(path):
    df = pd.read_csv(path)
    df = df.sort_values(by=["city", "timestamp"]).reset_index(drop=True)
    
    df_res = analyze_data_full(df)

    return df, df_res


async def get_weather_async(city, api_key=None):
    url = URL_TEMPLATE.format(
        city=city,
        API_KEY=api_key
    )
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
                content = await response.text()
                return json.loads(content)


def main():
    st.write("Current date: ", datetime.date.today())
    current_season = date_to_season(datetime.date.today())
    st.write(f"Current season: **{current_season}**")

    uploaded_file = st.file_uploader("Choose CSV-file", type=["csv"])
    if uploaded_file is None:
        st.write("Please upload your CSV-file.")
        return
    
    df_orig, df_stats = preprocessing(uploaded_file)

    city = st.selectbox("Select the city: ", df_orig["city"].unique())    
    api_key = st.text_input("Enter the api key for OpenWeather", None)
    
    if not api_key is None:
        weather = asyncio.run(get_weather_async(city, api_key))

        if "main" not in weather:
            st.error(weather["message"])
            return
        
        curr_temp = weather["main"]["temp"]
        
        normal_mean, normal_std = df_stats.loc[
                (df_stats.city == city) & (df_stats.season == "winter"), ["mean", "std"]
            ].values[0]
    
        lower_bound = normal_mean - 2 * normal_std
        upper_bound = normal_mean + 2 * normal_std

        is_anomaly = True if curr_temp > upper_bound or curr_temp < lower_bound else False
        
        if is_anomaly:
            st.error(f"Current temperature in {city}: **{curr_temp} °C**. IT IS AN ANOMALY!!!")
        else:
            st.success(f"Current temperature in {city}: **{curr_temp} °C**. Everything is fine.")
        

        fig, ax = plt.subplots(figsize=(10, 7))
        plt.title(f"Temperature distribution in {city}")
        sns.boxplot(df_stats.loc[df_stats.city == city], y="temperature", x="season", ax=ax)
        st.pyplot(fig)


        fig, ax = plt.subplots(figsize=(15, 8))
        plt.title(f"Historical temperature in {city}")

        df_slice = df_stats.loc[df_stats.city == city]
        df_slice.loc[:, "timestamp"] = pd.to_datetime(df_slice["timestamp"])
        df_anomaly = df_slice.loc[df_slice["is_anomaly"] == 1]

        ax.plot(df_slice["timestamp"], df_slice["temperature"], label="Temperature")
        ax.plot(df_slice["timestamp"], df_slice["lower_bound"], label="Normal temperature lower bound", linestyle='dashed')
        ax.plot(df_slice["timestamp"], df_slice["upper_bound"], label="Normal temperature upper bound", linestyle='dashed')
        ax.scatter(df_anomaly["timestamp"], df_anomaly["temperature"], color="red", marker="*", label="anomaly")

        ax.legend()
        st.pyplot(fig)
        
        st.write("А если вам кажется, что там, где вы сейчас находитесь очень холодно и вы хотите в более теплые края, то у меня есть для вас решение!!")




    

if __name__ == "__main__":
    
    # Смешная картинка, можно бонус поинт пж
    image = Image.open('assets/CAO.jpg')

    st.set_page_config(
        initial_sidebar_state="auto",
        page_title="OpenWeather Demo",
        page_icon=image,
    )

    col1, col2, col3 = st.columns(3)

    st.image(image)

    st.write(
        """
        ВСЕМ ПРИВЕТ!!!!!
        """
    )
    
    main()
