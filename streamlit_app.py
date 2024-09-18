import streamlit as st
from datetime import time, datetime

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

st.subheader('Range slider')

values = st.slider("Select a range of values",0.0, 100.0, (25.0,75.0))
st.write('Values:', values)

st.subheader('Range time slider')

appointment = st.slider(
    "Schedule your appointment:",
    value=(time(11,30),time(12,45)))
st.write("You're scheduled for:", appointment)

st.subheader('Datetime slider')

start_time = st.slider(
    "When do you start",
    value=datetime(2020,1,1,9,30),
    format="MM/DD/YY - hh:mm")
st.write("Start time:",start_time)

