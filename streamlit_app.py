import streamlit as st
st.set_page_config(page_title = "Data Sensemaking Demo")
st.title("I will complete by PhD successfully by September 2025")
st.caption("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.write("Have a nice day Ali!")

st.subheader('Slider')

age = st.slider('How old are you?', 0,130,25)
st.write("I'm", age, 'years old')