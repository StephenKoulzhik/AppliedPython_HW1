import streamlit as st
from PIL import Image
import datetime
import pandas as pd


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


def main():
    st.write("Today's date: ", datetime.date.today())
    st.write(f"Current season: **{date_to_season(datetime.date.today())}**")

    uploaded_file = st.file_uploader("Choose CSV-file", type=["csv"])
    if uploaded_file is None:
        st.write("Please upload your CSV-file.")
        return
    
    df_orig, df_stats = preprocessing(uploaded_file)

    city = st.selectbox("Select the city: ", df_orig["city"].unique())    
    api_key = st.text_input("Enter the api key for OpenWeather", "")



    

if __name__ == "__main__":
    image = Image.open('assets/CAO.jpg')

    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title="OpenWeather Demo",
        page_icon=image,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(' ')

    with col2:
        st.image(image)

    with col3:
        st.write(' ')


    st.write(
        """
        ВСЕМ ПРИВЕТ!!!!!
        """
    )
    
    main()
