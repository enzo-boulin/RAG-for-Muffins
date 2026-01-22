import streamlit as st
from muffin.main import main


BOT_NAME = "MC Muffin"
SUBWAY_SURFERS_URL = "https://www.youtube.com/watch?v=QPW3XwBoQlw"

st.set_page_config(page_title=BOT_NAME, page_icon="🧁")

st.title(f"🧁 {BOT_NAME}")
st.subheader("Yo ! Dis-moi ce qu'il y a dans ton frigo !")


user_prompt = st.text_input("Ingrédients (ex: chocolat, banane...)", "")

if st.button("Trouver un muffin"):
    if user_prompt:
        with st.spinner(f"{BOT_NAME} réfléchit..."):
            st.video(SUBWAY_SURFERS_URL, loop=True, autoplay=True, muted=True)
            st.markdown(main(user_prompt))
    else:
        st.warning("Veuillez entrer des ingrédients.")
