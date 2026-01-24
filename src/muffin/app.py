import logging
import random

import streamlit as st

from muffin.constant import LOGGING_LEVEL
from muffin.main import main

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)


BOT_NAME = "MC Muffin"
WAINTING_URLS = [
    "https://www.youtube.com/watch?v=QPW3XwBoQlw",
    "https://www.youtube.com/watch?v=u7kdVe8q5zs",
    "https://www.youtube.com/watch?v=nT4AtEvalSc",
    "https://www.youtube.com/watch?v=TuGv1WIyUK4",
]
WAINTING_URL = random.choice(WAINTING_URLS)

st.set_page_config(page_title=BOT_NAME, page_icon="🧁")

st.title(f"🧁 {BOT_NAME}")
st.subheader("Yo ! Dis-moi ce qu'il y a dans ton frigo !")

user_prompt = st.text_input("Ingrédients (ex: chocolat, banane...)", "")

placeholder = st.empty()

if st.button("Trouver un muffin"):
    if user_prompt:
        with placeholder.container():
            with st.spinner(f"{BOT_NAME} réfléchit..."):
                st.video(WAINTING_URL, loop=True, autoplay=True, muted=True)

                result = main(user_prompt)

        placeholder.empty()
        st.markdown(result)
    else:
        st.warning("Veuillez entrer des ingrédients.")
