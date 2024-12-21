import streamlit as st
from PIL import Image
import datetime


def date_to_season(date):
    if date.month in [12, 1, 2]:
        return "winter"
    elif date.month in [3, 4, 5]:
        return "spring"
    elif date.month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


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

    st.write("Today's date: ", datetime.date.today())
    st.write(f"Current season: *{date_to_season(datetime.date.today())}*")
