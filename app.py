import streamlit as st
from dotenv import  load_dotenv, find_dotenv
from PIL import Image

def main():
    st.set_page_config(
        page_title="Neuradev Coding Test Platform",
        page_icon="🧑🏾‍💻",
        initial_sidebar_state="collapsed"
    )
    st.header("Eugene AI Testing Platform")
    hero_image = Image.open('assets/images/starter.jpg')
    st.image(hero_image)


# Run the Streamlit app
if __name__ == '__main__':
    main()
