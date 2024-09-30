import streamlit as st
import pydeck as pdk
import pandas as pd
import json

# Always prompt the user to upload a JSON file
uploaded_file = st.file_uploader("Please upload a JSON file to proceed", type=["json"])

if uploaded_file is not None:
    # Reading the file once it's uploaded
    data = json.load(uploaded_file)

    # Extract relevant waypoints, locations, and activity types from the JSON data
    timeline_data = []
    all_waypoints = []
    
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
                'distance': distance / 1000,  # Convert to kilometers
                'waypoints': waypoints
            })

    # Display a table of all activities
    st.write("### Activities Summary")
    activity_df = pd.DataFrame(timeline_data)
    st.dataframe(activity_df[['activity', 'start_time', 'end_time', 'distance']])

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

    # Create a DataFrame for the waypoints and paths
    waypoint_df = pd.DataFrame(all_waypoints)

    # Set the initial view state for the map (centered on the waypoints)
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
        path_data = [{"path": activity['waypoints'], "name": activity['activity']} for activity in timeline_data]
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_data,
            get_path="path",
            get_width=path_width,  # Customizable width
            get_color=path_rgb_color,  # Customizable color
            width_min_pixels=path_width,
        )

        # Render the map with waypoints and paths for all activities
        st.pydeck_chart(pdk.Deck(
            initial_view_state=initial_view_state,
            layers=[scatter_layer, path_layer],
            tooltip={"text": "Activity: {activity}"}
        ))

else:
    st.warning("Please upload a JSON file to proceed.")

# Add a disclaimer at the bottom of the page
st.markdown("---")
st.markdown("**Disclaimer:** Please be advised that the information within this service is provided without liability.")