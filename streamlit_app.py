import streamlit as st
import pydeck as pdk
import pandas as pd
import json
from datetime import datetime, timedelta

# Convert the ISO timestamp into a pandas datetime object
def parse_iso_timestamp(timestamp):
    return pd.to_datetime(timestamp)

# Filter activities by date range
def filter_by_date_range(df, start_date, end_date):
    """Filter DataFrame by date range."""
    
    # Remove timezone from 'start_time' to make it timezone-naive
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.tz_convert(None)

    # Ensure start_date and end_date are timezone-naive as well
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # # Debugging: Check types to ensure they're all timezone-naive
    # st.write(f"Start date type: {type(start_date)}")
    # st.write(f"End date type: {type(end_date)}")
    # st.write(f"'start_time' column dtype: {df['start_time'].dtype}")

    # Filter rows where 'start_time' falls within the start_date and end_date
    mask = (df['start_time'] >= start_date) & (df['start_time'] <= end_date)

    # Return the filtered DataFrame, dropping NaT rows
    return df[mask].dropna(subset=['start_time'])

# Always prompt the user to upload a JSON file
uploaded_file = st.file_uploader("Please upload a JSON file to proceed", type=["json"])

# Header text for the page
st.header("_Google Maps_ timeline analyzer")

# Setup configuration for the page

st.set_page_config(
    page_title="Google Maps Timeline Analyser",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': ""
    # }
)

if uploaded_file is not None:
    # Reading the file once it's uploaded
    data = json.load(uploaded_file)

    # Extract relevant waypoints, locations, and activity types from the JSON data
    timeline_data = []
    all_waypoints = []
    
    for obj in data['timelineObjects']:
        if 'activitySegment' in obj and 'waypointPath' in obj['activitySegment']:
            activity_type = obj['activitySegment'].get('activityType', 'Unknown')
            start_time = parse_iso_timestamp(obj['activitySegment']['duration']['startTimestamp'])
            end_time = parse_iso_timestamp(obj['activitySegment']['duration']['endTimestamp'])
            duration = (end_time - start_time).total_seconds() / 60  # Duration in minutes
            distance = obj['activitySegment']['distance'] if 'distance' in obj['activitySegment'] else 0
            average_speed = (distance / 1000) / (duration / 60)  # Speed in km/h

            waypoints = []
            for waypoint in obj['activitySegment']['waypointPath']['waypoints']:
                lat = waypoint['latE7'] / 1e7  # Convert to proper latitude
                lng = waypoint['lngE7'] / 1e7  # Convert to proper longitude
                waypoints.append([lng, lat])  # Add longitude and latitude to path list
                all_waypoints.append({
                    'latitude': lat,
                    'longitude': lng,
                    'activity': activity_type
                })

            timeline_data.append({
                'activity': activity_type,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'distance': distance / 1000,  # Convert to kilometers
                'average_speed': average_speed,  # km/h
                'waypoints': waypoints
            })

    # Convert timeline data into a DataFrame
    activity_df = pd.DataFrame(timeline_data)

    # Filters: Time frame (default 1 week), activity type
    st.sidebar.header("Filters")

    # Get the min and max date from 'start_time'
    min_date = activity_df['start_time'].min().date()  # Get the earliest date in the dataset
    max_date = activity_df['start_time'].max().date()  # Get the latest date in the dataset

    # Date range filter
    # Restrict the date inputs to the file's time range
    start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    # Filter by activity type
    activity_types = activity_df['activity'].unique().tolist()
    selected_activity_types = st.sidebar.multiselect("Filter by Activity Type", options=activity_types, default=activity_types)

    # Apply the filters
    filtered_df = filter_by_date_range(activity_df, start_date, end_date)
    filtered_df = filtered_df[filtered_df['activity'].isin(selected_activity_types)]

    # Display filtered data in a table
    st.write("### Filtered Activities Summary")
    st.dataframe(filtered_df[['activity', 'start_time', 'end_time', 'distance', 'average_speed', 'duration']])

    # Overview of total distance
    total_distance = filtered_df['distance'].sum()
    st.write(f"**Total Distance:** {total_distance:.2f} km")

    # Waypoint and Path customization options
    waypoint_size = st.slider("Select Waypoint Size", min_value=0, max_value=100, value=20, key="waypoint_size")
    waypoint_color = st.color_picker("Pick Waypoint Color", value='#FF0000', key="waypoint_color")  # Default is red
    path_width = st.slider("Select Path Width", min_value=1, max_value=20, value=3, key="path_width")
    path_color = st.color_picker("Pick Path Color", value='#0000FF', key="path_color")  # Default is blue

    # Convert colors to RGB format for Pydeck
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

    waypoint_rgb_color = hex_to_rgb(waypoint_color)
    path_rgb_color = hex_to_rgb(path_color)

    # Create a DataFrame for the waypoints
    all_waypoints = []
    path_data = []
    for index, row in filtered_df.iterrows():
        for waypoint in row['waypoints']:
            all_waypoints.append({'latitude': waypoint[1], 'longitude': waypoint[0], 'activity': row['activity']})
        path_data.append({"path": row['waypoints'], "name": row['activity']})

    waypoint_df = pd.DataFrame(all_waypoints)

    # Map display
    if not waypoint_df.empty:
        initial_view_state = pdk.ViewState(
            latitude=waypoint_df['latitude'].mean(),
            longitude=waypoint_df['longitude'].mean(),
            zoom=12,
            pitch=0,
        )

        # Scatter layer for waypoints
        scatter_layer = pdk.Layer(
            'ScatterplotLayer',
            data=waypoint_df,
            get_position='[longitude, latitude]',
            get_radius=waypoint_size,  # Customizable size
            get_color=waypoint_rgb_color,  # Customizable color
            pickable=True,
        )

        # Line layer for paths
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_data,
            get_path="path",
            get_width=path_width,  # Customizable width
            get_color=path_rgb_color,  # Customizable color
            width_min_pixels=path_width,
        )

        # Render the map with waypoints and paths
        st.pydeck_chart(pdk.Deck(
            initial_view_state=initial_view_state,
            layers=[scatter_layer, path_layer],
            tooltip={"text": "Activity: {activity}"}
        ))

else:
    st.warning("Please upload a JSON file to proceed.")

# Add a disclaimer at the bottom of the page
st.markdown("---")
st.markdown("**Disclaimer:**Please be advised that the information within this service is provided without liability.")
st.markdown("**Developed by [Pavithren V S Pakianathan](https://www.pavithren.com)**")
