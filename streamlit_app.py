import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import time

# Always prompt the user to upload a JSON file
uploaded_file = st.file_uploader("Please upload a JSON file to proceed", type=["json"])

if uploaded_file is not None:
    # Reading the file once it's uploaded
    data = json.load(uploaded_file)

    # Extract relevant waypoints, locations, and activity types from the JSON data
    timeline_data = []
    for obj in data['timelineObjects']:
        if 'activitySegment' in obj and 'waypointPath' in obj['activitySegment']:
            activity_type = obj['activitySegment'].get('activityType', 'Unknown')
            start_time = obj['activitySegment']['duration']['startTimestamp']
            end_time = obj['activitySegment']['duration']['endTimestamp']
            distance = obj['activitySegment']['distance'] if 'distance' in obj['activitySegment'] else 0

            waypoints = []
            for waypoint in obj['activitySegment']['waypointPath']['waypoints']:
                lat = waypoint['latE7'] / 1e7  # Convert to proper latitude
                lng = waypoint['lngE7'] / 1e7  # Convert to proper longitude
                waypoints.append([lng, lat])

            timeline_data.append({
                'activity': activity_type,
                'start_time': start_time,
                'end_time': end_time,
                'distance': distance,
                'waypoints': waypoints
            })

    # Sidebar: Option to scroll through timeline or play activities
    st.sidebar.title("Timeline Control")
    activity_index = st.sidebar.slider("Select Activity", min_value=0, max_value=len(timeline_data) - 1, value=0)

    # Add a play button to automatically move through activities
    if st.sidebar.button("Play"):
        for i in range(len(timeline_data)):
            st.sidebar.slider("Select Activity", min_value=0, max_value=len(timeline_data) - 1, value=i)
            time.sleep(1)  # Pause for 1 second between activities

    # Get the current activity's waypoints and data
    selected_activity = timeline_data[activity_index]
    waypoints = selected_activity['waypoints']

    # Waypoint and Path customization options
    waypoint_size = st.slider("Select Waypoint Size", min_value=50, max_value=1000, value=100)
    waypoint_color = st.color_picker("Pick Waypoint Color", value='#FF0000')  # Default is red
    path_width = st.slider("Select Path Width", min_value=1, max_value=20, value=3)
    path_color = st.color_picker("Pick Path Color", value='#0000FF')  # Default is blue

    # Convert colors to RGB format for Pydeck
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

    waypoint_rgb_color = hex_to_rgb(waypoint_color)
    path_rgb_color = hex_to_rgb(path_color)

    # Create a DataFrame for the waypoints
    waypoint_df = pd.DataFrame(waypoints, columns=['longitude', 'latitude'])

    # Set the initial view state for the map
    if not waypoint_df.empty:
        initial_view_state = pdk.ViewState(
            latitude=waypoint_df['latitude'].mean(),
            longitude=waypoint_df['longitude'].mean(),
            zoom=12,  # Adjust zoom based on the spread of points
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
            data=[{
                "path": waypoints,
                "name": selected_activity['activity']
            }],
            get_path="path",
            get_width=path_width,  # Customizable width
            get_color=path_rgb_color,  # Customizable color
            width_min_pixels=path_width,
        )

        # Render the map with the selected activity's waypoints and paths
        st.pydeck_chart(pdk.Deck(
            initial_view_state=initial_view_state,
            layers=[scatter_layer, path_layer],
            tooltip={"text": "Activity: " + selected_activity['activity']}
        ))

    # Display activity info
    st.write(f"Activity: {selected_activity['activity']}")
    st.write(f"Start Time: {selected_activity['start_time']}")
    st.write(f"End Time: {selected_activity['end_time']}")
    st.write(f"Distance: {selected_activity['distance'] / 1000:.2f} km")

else:
    st.warning("Please upload a JSON file to proceed.")

# Add a disclaimer at the bottom of the page
st.markdown("---")
st.markdown("**Disclaimer:** Please be advised that the information within this service is provided without liability.")