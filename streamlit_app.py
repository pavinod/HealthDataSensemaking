import streamlit as st
import pydeck as pdk
import pandas as pd
import json
from datetime import datetime

def filter_by_date_range(df, start_date, end_date):
    """Filter DataFrame by date range."""
    # Ensure 'start_time' column is in datetime format
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')

    # Convert start_date and end_date to timezone-aware datetime objects (UTC)
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')

    # Filter rows where 'start_time' falls within the start_date and end_date
    mask = (df['start_time'] >= start_date) & (df['start_time'] <= end_date)
    
    # Return the filtered DataFrame, dropping NaT rows
    return df[mask].dropna(subset=['start_time'])


def render_map(waypoint_df, path_data, waypoint_size, waypoint_rgb_color, path_width, path_rgb_color, use_satellite):
    """Render the map with waypoints and paths."""
    # Define the initial view state
    if waypoint_df is not None and not waypoint_df.empty:
        initial_view_state = pdk.ViewState(
            latitude=waypoint_df['latitude'].mean(),
            longitude=waypoint_df['longitude'].mean(),
            zoom=12,
            pitch=0,
        )
    else:
        initial_view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=2,
            pitch=0,
        )

    # Use satellite view if selected
    map_style = "mapbox://styles/mapbox/satellite-v9" if use_satellite else "mapbox://styles/mapbox/streets-v11"

    # Scatter layer for waypoints if available
    layers = []
    if waypoint_df is not None and not waypoint_df.empty:
        scatter_layer = pdk.Layer(
            'ScatterplotLayer',
            data=waypoint_df,
            get_position='[longitude, latitude]',
            get_radius=waypoint_size,  # Customizable size
            get_color=waypoint_rgb_color,  # Customizable color
            pickable=True,
        )
        layers.append(scatter_layer)

    # Line layer for paths if available
    if path_data is not None and len(path_data) > 0:
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_data,
            get_path="path",
            get_width=path_width,  # Customizable width
            get_color=path_rgb_color,  # Customizable color
            width_min_pixels=path_width,
        )
        layers.append(path_layer)

    # Render the map with waypoints and paths (if available)
    st.pydeck_chart(pdk.Deck(
        initial_view_state=initial_view_state,
        layers=layers,
        map_style=map_style,  # Switch between satellite and street view
        tooltip={"text": "Activity: {activity}"}
    ))


def main():
    st.title("Activity Map Visualization")

    # Always prompt the user to upload a JSON file
    uploaded_file = st.file_uploader("Please upload a JSON file to proceed", type=["json"])

    waypoint_df = None
    path_data = []

    # If a file is uploaded, process the data
    if uploaded_file is not None:
        # Reading the file once it's uploaded
        data = json.load(uploaded_file)

        # Process the data and convert to DataFrame as before
        processor = ActivityProcessor(data)
        activity_df = processor.activity_df

        # Calculate duration in hours and minutes
        activity_df['duration_hours'] = activity_df['duration'] // 60  # Hours
        activity_df['duration_minutes'] = activity_df['duration'] % 60  # Minutes

        # Convert distance to km with 2 decimal points
        activity_df['distance'] = activity_df['distance'].round(2)

        # Format average speed to 2 decimal places (km/h)
        activity_df['average_speed'] = activity_df['average_speed'].round(2)

        # Get the min and max date from 'start_time'
        min_date = activity_df['start_time'].min().date()  # Earliest date in the dataset
        max_date = activity_df['start_time'].max().date()  # Latest date in the dataset

        # Restrict the date inputs to the file's time range
        start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # Filter data based on date range
        filtered_df = filter_by_date_range(activity_df, start_date, end_date)

        # Display filtered data with correct formatting
        st.write("Filtered Activities")
        st.dataframe(filtered_df[['activity', 'start_time', 'end_time', 'distance', 'average_speed', 'duration_hours', 'duration_minutes']])

        # Get waypoints and path data for the filtered activities
        waypoint_df, path_data = processor.get_waypoints_for_filtered_data(filtered_df)

    # Waypoint and Path customization options
    waypoint_size = st.slider("Select Waypoint Size", min_value=0, max_value=100, value=20)
    waypoint_color = st.color_picker("Pick Waypoint Color", value='#FF0000')  # Default is red
    path_width = st.slider("Select Path Width", min_value=1, max_value=20, value=3)
    path_color = st.color_picker("Pick Path Color", value='#0000FF')  # Default is blue

    # Convert colors to RGB format
    waypoint_rgb_color = hex_to_rgb(waypoint_color)
    path_rgb_color = hex_to_rgb(path_color)

    # Toggle for satellite view
    use_satellite = st.checkbox("Use Satellite View", value=False)

    # Always render the map, even if there's no data
    render_map(waypoint_df, path_data, waypoint_size, waypoint_rgb_color, path_width, path_rgb_color, use_satellite)

    # Add a disclaimer at the bottom of the page
    st.markdown("---")
    st.markdown("**Disclaimer:** Please be advised that the information within this service is provided without liability.")


if __name__ == "__main__":
    main()