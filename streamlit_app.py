import streamlit as st
from datetime import time, datetime
import pandas as pd
import ydata_profiling
from ydata_profiling import ProfileReport
import numpy as np

#https://pavithren.streamlit.app/
#stenv miniconda3 3e.9.19


st.header('`streamlit_pandas_profiling')

df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/penguins_cleaned.csv')
pr = df.profile_report()
st_profile_report(pr)

#day 12

# st.header('st.checkbox')

# st.write('What would you like to order?')

# icecream = st.checkbox ('Ice cream')
# coffee = st.checkbox ('Coffeeeeee')
# cola = st.checkbox ('Cola')

# if icecream:
#     st.write("Great! Here's some more 🍦")
# if coffee:
#     st.write("Okay, here's some coffee ☕")
# if cola:
#     st.write("Here you go 🥤")


#Day 11
# st.set_page_config(page_title = "Data Sensemaking Practice")
# st.title("I will complete by PhD successfully by September 2025")

# st.header('st.multiselect')

# options = st.multiselect('What are you favourite colors',['Green','Yellow','Red','Blue'],['Yellow','Red'])

# st.write('You selected:',options)

#Day 10
# st.header('st.selectbox')
# option = st.selectbox('what is your favourite color?', ("blue","green","red",))
# st.write('Your favourite color is ',option)


# st.header('Line chart')

# chart_data = pd.DataFrame(
#     np.random.randn(20,3),
#     columns = ['a','b','c']
# )

# st.line_chart(chart_data)

# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )
# st.write("Have a nice day Ali!")

# st.subheader('Slider')

# age = st.slider('How old are you?', 0,130,25)
# st.write("I'm", age, 'years old')

# st.subheader('Range slider')

# values = st.slider("Select a range of values",0.0, 100.0, (25.0,75.0))
# st.write('Values:', values)

# st.subheader('Range time slider')

# appointment = st.slider(
#     "Schedule your appointment:",
#     value=(time(11,30),time(12,45)))
# st.write("You're scheduled for:", appointment)

# st.subheader('Datetime slider')

# start_time = st.slider(
#     "When do you start",
#     value=datetime(2020,1,1,9,30),
#     format="MM/DD/YY - hh:mm")
# st.write("Start time:",start_time)

footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: gray;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://www.pavithren.com/" target="_blank">Pavithren (Viren) V S Pakianathan</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

