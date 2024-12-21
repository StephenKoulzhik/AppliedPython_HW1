import streamlit as st
from PIL import Image
import datetime


if __name__ == "__main__":
    image = Image.open('assets/CAO.jpg')

    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title="OpenWeather Demo",
        page_icon=image,
    )

    st.image(image)

    st.write(
        """
        ВСЕМ ПРИВЕТ!!!!!
        """
    )

    st.write("Today's date: ", datetime.today())
    st.write("Current season is: ____")