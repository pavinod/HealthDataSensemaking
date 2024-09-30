import streamlit as st
import pydeck as pdk
import pandas as pd
import json

# Always prompt the user to upload a JSON file
uploaded_file = st.file_uploader("Please upload a JSON file to proceed", type=["json"])

if uploaded_file is not None:
    # Reading the file once it's uploaded
    data = json.load(uploaded_file)

    # Extracting relevant waypoints, locations, and activity types from the JSON data
    waypoints_data = []
    for obj in data['timelineObjects']:
        if 'activitySegment' in obj and 'waypointPath' in obj['activitySegment']:
            activity_type = obj['activitySegment'].get('activityType', 'Unknown')
            start_time = obj['activitySegment']['duration']['startTimestamp']
            end_time = obj['activitySegment']['duration']['endTimestamp']
            distance = obj['activitySegment']['distance'] if 'distance' in obj['activitySegment'] else 0
            for waypoint in obj['activitySegment']['waypointPath']['waypoints']:
                lat = waypoint['latE7'] / 1e7  # Convert to proper latitude
                lng = waypoint['lngE7'] / 1e7  # Convert to proper longitude
                waypoints_data.append({
                    'latitude': lat,
                    'longitude': lng,
                    'activity': activity_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'distance': distance
                })

    # Create a DataFrame for Pydeck
    df = pd.DataFrame(waypoints_data)

    # Debugging: Display the first few rows of data
    st.write(df.head())  # Check if the coordinates are being parsed correctly

    # Waypoint configuration options
    waypoint_size = st.slider("Select Waypoint Size", min_value=50, max_value=1000, value=100)
    waypoint_color = st.color_picker("Pick Waypoint Color", value='#FF0000')  # Default is red

    # Path configuration options
    show_paths = st.checkbox("Show Paths", value=True)
    path_width = st.slider("Select Path Width", min_value=1, max_value=20, value=3)
    path_color = st.color_picker("Pick Path Color", value='#0000FF')  # Default is blue

    # Convert colors to RGB format for Pydeck
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

    waypoint_rgb_color = hex_to_rgb(waypoint_color)
    path_rgb_color = hex_to_rgb(path_color)

    # Set the initial view state for the map (centered on the first waypoint of filtered data)
    if not df.empty:
        initial_view_state = pdk.ViewState(
            latitude=df['latitude'].mean(),
            longitude=df['longitude'].mean(),
            zoom=12,  # Adjust zoom based on the spread of points
            pitch=0,
        )

        # Scatter layer for waypoints
        scatter_layer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[longitude, latitude]',
            get_radius=waypoint_size,  # Customizable size
            get_color=waypoint_rgb_color,  # Customizable color
            pickable=True,
        )

        layers = [scatter_layer]  # Start with waypoints

        if show_paths:
            line_layer = pdk.Layer(
                "LineLayer",
                data=df,
                get_source_position="[longitude, latitude]",
                get_target_position="[longitude, latitude]",
                get_color=path_rgb_color,  # Customizable color
                get_width=path_width,  # Customizable width
            )
            layers.append(line_layer)

        # Render the map
        st.pydeck_chart(pdk.Deck(
            initial_view_state=initial_view_state,
            layers=layers,
            tooltip={"text": "Activity: {activity}\nLat: {latitude}\nLng: {longitude}"}
        ))
    else:
        st.error("No waypoints available to display on the map.")

else:
    st.warning("Please upload a JSON file to proceed.")

# import streamlit as st
# from datetime import time, datetime
# import pandas as pd
# import ydata_profiling
# from streamlit_pandas_profiling import st_profile_report
# import numpy as np

# #https://pavithren.streamlit.app/
# #stenv miniconda3 3e.9.19

# #day 17
# st.title('Secret')
# st.write(st.secrets['message'])

# #day 16
# # st.set_page_config(page_title = "Data Sensemaking Practice")
# # st.title("I will complete by PhD successfully by September 2025")

# # st.code("""  
# # [theme]
# # primaryColor="#F39C12"
# # backgroundColor="#2E86C1"
# # secondaryBackgroundColor="#AED6F1"
# # textColor="#FFFFFF"
# # font="monospace"
# # """)

# # number = st.sidebar.slider("Select a number:", 0,10 , 5)
# # st.write('Selected number from slider widget is:', number)


# #day 14 issues with ydata/pandaprofiling: https://discuss.streamlit.io/t/pydantic-import-error-for-an-old-repo/61580/2
# # st.header('`streamlit_pandas_profiling')

# # df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/penguins_cleaned.csv')
# # pr = df.profile_report()
# # st_profile_report(pr)

# #day 12

# # st.header('st.checkbox')

# # st.write('What would you like to order?')

# # icecream = st.checkbox ('Ice cream')
# # coffee = st.checkbox ('Coffeeeeee')
# # cola = st.checkbox ('Cola')

# # if icecream:
# #     st.write("Great! Here's some more 🍦")
# # if coffee:
# #     st.write("Okay, here's some coffee ☕")
# # if cola:
# #     st.write("Here you go 🥤")


# #Day 11


# # st.header('st.multiselect')

# # options = st.multiselect('What are you favourite colors',['Green','Yellow','Red','Blue'],['Yellow','Red'])

# # st.write('You selected:',options)

# #Day 10
# # st.header('st.selectbox')
# # option = st.selectbox('what is your favourite color?', ("blue","green","red",))
# # st.write('Your favourite color is ',option)


# # st.header('Line chart')

# # chart_data = pd.DataFrame(
# #     np.random.randn(20,3),
# #     columns = ['a','b','c']
# # )

# # st.line_chart(chart_data)

# # st.write(
# #     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# # )
# # st.write("Have a nice day Ali!")

# # st.subheader('Slider')

# # age = st.slider('How old are you?', 0,130,25)
# # st.write("I'm", age, 'years old')

# # st.subheader('Range slider')

# # values = st.slider("Select a range of values",0.0, 100.0, (25.0,75.0))
# # st.write('Values:', values)

# # st.subheader('Range time slider')

# # appointment = st.slider(
# #     "Schedule your appointment:",
# #     value=(time(11,30),time(12,45)))
# # st.write("You're scheduled for:", appointment)

# # st.subheader('Datetime slider')

# # start_time = st.slider(
# #     "When do you start",
# #     value=datetime(2020,1,1,9,30),
# #     format="MM/DD/YY - hh:mm")
# # st.write("Start time:",start_time)

# footer="""<style>
# a:link , a:visited{
# color: blue;
# background-color: transparent;
# text-decoration: underline;
# }

# a:hover,  a:active {
# color: red;
# background-color: transparent;
# text-decoration: underline;
# }

# .footer {
# position: fixed;
# left: 0;
# bottom: 0;
# width: 100%;
# background-color: gray;
# color: black;
# text-align: center;
# }
# </style>
# <div class="footer">
# <p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://www.pavithren.com/" target="_blank">Pavithren (Viren) V S Pakianathan</a></p>
# </div>
# """
# st.markdown(footer,unsafe_allow_html=True)

