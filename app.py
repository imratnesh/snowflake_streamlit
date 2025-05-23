import streamlit as st
import json
import pandas as pd
import plotly.express as px
from PIL import Image
import io
import requests
import snowflake.connector
from dotenv import load_dotenv
import os
import asyncio

# Page config
st.set_page_config(
    page_title="Indian Cultural Heritage Explorer",
    page_icon="🏛️",
    layout="wide"
)

# Load environment variables
load_dotenv()
# print(os.getenv('SNOWFLAKE_USER'))
# print(os.getenv('SNOWFLAKE_PASSWORD'))
# print(os.getenv('SNOWFLAKE_ACCOUNT'))
# print(os.getenv('SNOWFLAKE_WAREHOUSE'))
# print(os.getenv('SNOWFLAKE_DATABASE'))
# print(os.getenv('SNOWFLAKE_SCHEMA'))


# Initialize Snowflake connection
def init_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            insecure_mode=True  # Only for testing
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return None


# Load forts data
@st.cache_data
def load_forts_data():
    try:
        with open('indian_forts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading forts data: {str(e)}")
        return []

# Main app
def main():
    st.title("🏛️ Indian Cultural Heritage Explorer")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Forts Explorer", "Cultural Insights", "Tourism Data"])
    
    if page == "Forts Explorer":
        show_forts_explorer()
    elif page == "Cultural Insights":
        show_cultural_insights()
    else:
        show_tourism_data()


def show_forts_explorer():
    st.header("Historical Forts of India")
    
    # Define states with tourism data (in lowercase for case-insensitive matching)
    tourism_states = {
        'andhra pradesh', 'gujarat', 'jharkhand', 'karnataka', 
        'madhya pradesh', 'maharashtra', 'punjab', 'rajasthan', 
        'tamil nadu', 'telengana', 'uttar pradesh', 'west bengal'
    }
    
    # Load data
    forts_data = load_forts_data()
    if not forts_data:
        st.warning("No forts data available.")
        return
    
    # Connect to Snowflake for tourism data
    conn = init_snowflake_connection()
    tourism_data = None
    if conn:
        try:
            query = """
            SELECT *
            FROM "TOP_10_STATE_VISIT"
            LIMIT 10
            """
            tourism_data = pd.read_sql(query, conn)
        except Exception as e:
            st.error(f"Error fetching tourism data: {str(e)}")
        finally:
            conn.close()
    
    # Data validation and cleaning
    valid_forts = []
    for fort in forts_data:
        if all(key in fort for key in ['id', 'name', 'locations', 'details']):
            # Clean locations data
            if isinstance(fort['locations'], list) and len(fort['locations']) > 0:
                # Extract state from location entries
                found_state = None
                for location in fort['locations']:
                    # Split location by comma and check each part
                    parts = [part.strip().lower() for part in location.split(',')]
                    # Check each part for a matching state
                    for part in parts:
                        if part in tourism_states:
                            found_state = part
                            break
                    if found_state:
                        break
                
                if found_state:
                    fort['state'] = found_state.title()  # Convert back to title case
                    valid_forts.append(fort)
    
    if not valid_forts:
        st.error("No valid fort data found for states with tourism data.")
        return
    
    # Create filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter by state - only show states with tourism data
        selected_state = st.selectbox(
            "Select Location", 
            ["All States"] + sorted([state.title() for state in tourism_states])
        )
    
    with col2:
        # Filter by type
        types = set()
        for fort in valid_forts:
            if fort.get('details', {}).get('Type'):
                types.add(fort['details']['Type'])
        
        selected_type = st.selectbox("Select Fort Type", ["All"] + sorted(list(types)))
    
    with col3:
        # Sort options
        sort_by = st.selectbox("Sort By", 
                             ["Name", "Last Updated", "Built Year"],
                             index=0)
    
    # Filter forts based on selection
    filtered_forts = valid_forts
    if selected_state != "All States":
        filtered_forts = [fort for fort in filtered_forts 
                         if fort.get('state') == selected_state]
    
    if selected_type != "All":
        filtered_forts = [fort for fort in filtered_forts 
                         if fort.get('details', {}).get('Type') == selected_type]
    
    # Sort forts
    if sort_by == "Name":
        filtered_forts.sort(key=lambda x: x.get('name', ''))
    elif sort_by == "Last Updated":
        filtered_forts.sort(key=lambda x: x.get('last_edited', ''), reverse=True)
    elif sort_by == "Built Year":
        filtered_forts.sort(key=lambda x: x.get('details', {}).get('Founded', ''))
    
    # Display state tourism statistics if available
    if tourism_data is not None and selected_state != "All States":
        st.subheader(f"Tourism Statistics for {selected_state}")
        # Find the state's rank and visits in tourism data
        state_stats = None
        for i in range(1, 11):
            state_col = f'TOP{i}_STATE'
            ftv_col = f'TOP{i}_FTV'
            if state_col in tourism_data.columns and ftv_col in tourism_data.columns:
                if tourism_data[state_col].iloc[0].lower() == selected_state.lower():
                    state_stats = {
                        'rank': i,
                        'visits': tourism_data[ftv_col].iloc[0]
                    }
                    break
        
        if state_stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tourism Rank", f"#{state_stats['rank']}")
            with col2:
                st.metric("Foreign Tourist Visits", f"{state_stats['visits']:,.0f}")
    
    # Display forts
    for fort in filtered_forts:
        with st.expander(f"{fort['name']} (ID: {fort['id']})"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if fort.get('images'):
                    try:
                        # Try to get the first non-icon image
                        image_url = next((img for img in fort['images'] 
                                       if not any(x in img.lower() 
                                                for x in ['icon', 'symbol', 'location_map'])), 
                                       fort['images'][0])
                        response = requests.get(image_url, timeout=5)
                        image = Image.open(io.BytesIO(response.content))
                        st.image(image, use_column_width=True)
                    except Exception:
                        st.write("Image not available")
            
            with col2:
                # Location information
                if fort.get('locations'):
                    st.write("**Location:** ", fort['locations'][0])
                
                # Details section
                if fort.get('details'):
                    details = fort['details']
                    st.write("**Type:** ", details.get('Type', 'N/A'))
                    st.write("**Founded:** ", details.get('Founded', 'N/A'))
                    st.write("**Status:** ", details.get('Abandoned', 'N/A'))
                    st.write("**Area:** ", details.get('Area', 'N/A'))
                    st.write("**Height:** ", details.get('Height', 'N/A'))
                    st.write("**Ownership:** ", details.get('Ownership', 'N/A'))
                    
                    if details.get('Coordinates'):
                        st.write("**Coordinates:** ", details['Coordinates'])
                        try:
                            # Parse coordinates from the format "18°34′54″N 83°22′00″E"
                            coord_str = details['Coordinates'].split('/')[0].strip()
                            lat_str = coord_str.split()[0]
                            lon_str = coord_str.split()[1]
                            
                            # Convert to decimal degrees
                            lat = float(lat_str[:-1]) * (1 if 'N' in lat_str else -1)
                            lon = float(lon_str[:-1]) * (1 if 'E' in lon_str else -1)
                            
                            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                        except Exception:
                            pass
                
                # Last edit information
                if fort.get('last_edited'):
                    st.write("**Last Updated:** ", fort['last_edited'])


def show_cultural_insights():
    st.header("Cultural Insights")
    
    # Connect to Snowflake
    conn = init_snowflake_connection()
    if conn:
        try:
            # Example query - replace with your actual query
            query = """
            SELECT *
            FROM "TOP_10_STATE_VISIT"
            LIMIT 10
            """
            df = pd.read_sql(query, conn)
            
            # Display insights
            st.subheader("Cultural Heritage Statistics")
            
            # Add filters
            show_raw_data = st.checkbox("Show Raw Data", value=False)
            
            if show_raw_data:
                st.dataframe(df)
            
            # Add visualizations
            if not df.empty:
                # Create a new dataframe for visualization
                viz_data = []
                for i in range(1, 11):
                    state_col = f'TOP{i}_STATE'
                    ftv_col = f'TOP{i}_FTV'
                    if state_col in df.columns and ftv_col in df.columns:
                        viz_data.append({
                            'State': df[state_col].iloc[0],
                            'Foreign Tourist Visits': df[ftv_col].iloc[0],
                            'Rank': i
                        })
                
                viz_df = pd.DataFrame(viz_data)
                
                # Calculate statistics
                total_visits = viz_df['Foreign Tourist Visits'].sum()
                avg_visits = viz_df['Foreign Tourist Visits'].mean()
                max_visits = viz_df['Foreign Tourist Visits'].max()
                min_visits = viz_df['Foreign Tourist Visits'].min()
                
                # Display statistics
                st.subheader("Key Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Visits", f"{total_visits:,.0f}")
                with col2:
                    st.metric("Average Visits", f"{avg_visits:,.0f}")
                with col3:
                    st.metric("Maximum Visits", f"{max_visits:,.0f}")
                with col4:
                    st.metric("Minimum Visits", f"{min_visits:,.0f}")
                
                # Create bar chart with enhanced interactivity
                fig = px.bar(
                    viz_df,
                    x='State',
                    y='Foreign Tourist Visits',
                    title='Top 10 States by Foreign Tourist Visits',
                    color='Rank',
                    color_continuous_scale='Viridis',
                    hover_data={
                        'State': True,
                        'Foreign Tourist Visits': ':,.0f',
                        'Rank': True,
                        'Percentage': viz_df['Foreign Tourist Visits'] / total_visits * 100
                    }
                )
                fig.update_layout(
                    xaxis_title="State",
                    yaxis_title="Number of Foreign Tourist Visits",
                    showlegend=False,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Add pie chart with enhanced interactivity
                fig2 = px.pie(
                    viz_df,
                    values='Foreign Tourist Visits',
                    names='State',
                    title='Distribution of Foreign Tourist Visits by State',
                    hover_data={
                        'State': True,
                        'Foreign Tourist Visits': ':,.0f',
                        'Percentage': viz_df['Foreign Tourist Visits'] / total_visits * 100
                    }
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)
                
                # Add map visualization
                st.subheader("Geographic Distribution")
                # Note: This is a placeholder for map visualization
                # You would need to add state coordinates to create an actual map
                st.info("Map visualization requires state coordinates data")
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            conn.close()
    else:
        st.warning("Please configure Snowflake credentials to view cultural insights.")

def show_tourism_data():
    st.header("Tourism Data Analysis")
    
    # Connect to Snowflake
    conn = init_snowflake_connection()
    if conn:
        try:
            # Example query - replace with your actual query
            query = """
            SELECT *
            FROM "HACKEREARTH_YOURSTORY"."PUBLIC"."COUNTRY_WISE_YEARLY_VISITORS"
            LIMIT 10
            """
            df = pd.read_sql(query, conn)
            
            # Display tourism data
            st.subheader("Tourism Statistics")
            
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                show_raw_data = st.checkbox("Show Raw Data", value=False)
            with col2:
                selected_countries = st.multiselect(
                    "Select Countries",
                    options=df['COUNTRY'].unique(),
                    default=df['COUNTRY'].unique()[:3]
                )
            
            if show_raw_data:
                st.dataframe(df)
            
            # Add visualizations
            if not df.empty:
                # Melt the dataframe to convert year columns into rows
                df_melted = pd.melt(
                    df,
                    id_vars=['COUNTRY'],
                    value_vars=['YEAR2014', 'YEAR2015', 'YEAR2016', 'YEAR2017', 
                              'YEAR2018', 'YEAR2019', 'YEAR2020'],
                    var_name='YEAR',
                    value_name='VISITORS'
                )
                
                # Clean up year column by removing 'YEAR' prefix
                df_melted['YEAR'] = df_melted['YEAR'].str.replace('YEAR', '')
                
                # Filter selected countries
                if selected_countries:
                    df_melted = df_melted[df_melted['COUNTRY'].isin(selected_countries)]
                
                # Calculate year-over-year growth
                df_melted['YoY_Growth'] = df_melted.groupby('COUNTRY')['VISITORS'].pct_change() * 100
                
                # Calculate statistics
                total_visits = df_melted['VISITORS'].sum()
                avg_visits = df_melted['VISITORS'].mean()
                max_visits = df_melted['VISITORS'].max()
                min_visits = df_melted['VISITORS'].min()
                
                # Display statistics
                st.subheader("Key Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Visits", f"{total_visits:,.0f}")
                with col2:
                    st.metric("Average Visits", f"{avg_visits:,.0f}")
                with col3:
                    st.metric("Maximum Visits", f"{max_visits:,.0f}")
                with col4:
                    st.metric("Minimum Visits", f"{min_visits:,.0f}")
                
                # Create line plot with enhanced interactivity
                fig = px.line(
                    df_melted,
                    x='YEAR',
                    y='VISITORS',
                    color='COUNTRY',
                    title='Tourist Visits by Country Over Time',
                    hover_data={
                        'COUNTRY': True,
                        'YEAR': True,
                        'VISITORS': ':,.0f',
                        'YoY_Growth': ':,.1f%'
                    }
                )
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Visitors",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Add bar chart for top countries with enhanced interactivity
                top_countries = df_melted.groupby('COUNTRY')['VISITORS'].sum().nlargest(5)
                top_countries_df = pd.DataFrame({
                    'Country': top_countries.index,
                    'Total Visitors': top_countries.values,
                    'Percentage': (top_countries.values / total_visits * 100)
                })
                
                fig2 = px.bar(
                    top_countries_df,
                    x='Country',
                    y='Total Visitors',
                    title='Top 5 Countries by Total Visitors',
                    hover_data={
                        'Country': True,
                        'Total Visitors': ':,.0f',
                        'Percentage': ':,.1f%'
                    }
                )
                fig2.update_layout(
                    xaxis_title="Country",
                    yaxis_title="Total Visitors",
                    hovermode='x unified'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Add year-over-year growth visualization
                st.subheader("Year-over-Year Growth Analysis")
                fig3 = px.bar(
                    df_melted,
                    x='YEAR',
                    y='YoY_Growth',
                    color='COUNTRY',
                    title='Year-over-Year Growth by Country',
                    labels={'YoY_Growth': 'Growth Rate (%)'},
                    hover_data={
                        'COUNTRY': True,
                        'YEAR': True,
                        'YoY_Growth': ':,.1f%',
                        'VISITORS': ':,.0f'
                    }
                )
                fig3.update_layout(hovermode='x unified')
                st.plotly_chart(fig3, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            conn.close()
    else:
        st.warning("Please configure Snowflake credentials to view tourism data.")


if __name__ == "__main__":
    main() 