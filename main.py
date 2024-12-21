import streamlit as st
from PIL import Image

if __name__ == "__main__":
    image = Image.open('assets/CAO.jpg')

    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title="Demo Titanic",
        page_icon=image,

    )

    st.image(image)