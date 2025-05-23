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

# Page config
st.set_page_config(
    page_title="Indian Cultural Heritage Explorer",
    page_icon="🏛️",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize Snowflake connection
def init_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return None

# Load forts data
@st.cache_data
def load_forts_data():
    with open('indian_forts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

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
    
    # Load data
    forts_data = load_forts_data()
    
    # Create filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by state
        states = list(set(fort.get('details', {}).get('Location', '').split(',')[-1].strip() for fort in forts_data if fort.get('details', {}).get('Location')))
        selected_state = st.selectbox("Select State", ["All"] + sorted(states))
    
    with col2:
        # Filter by type
        types = list(set(fort.get('details', {}).get('Type', '') for fort in forts_data if fort.get('details', {}).get('Type')))
        selected_type = st.selectbox("Select Fort Type", ["All"] + sorted(types))
    
    # Filter forts based on selection
    filtered_forts = forts_data
    if selected_state != "All":
        filtered_forts = [fort for fort in filtered_forts if selected_state in fort.get('details', {}).get('Location', '')]
    if selected_type != "All":
        filtered_forts = [fort for fort in filtered_forts if selected_type == fort.get('details', {}).get('Type', '')]
    
    # Display forts
    for fort in filtered_forts:
        with st.expander(fort['name']):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if fort.get('images'):
                    try:
                        response = requests.get(fort['images'][0])
                        image = Image.open(io.BytesIO(response.content))
                        st.image(image, use_column_width=True)
                    except:
                        st.write("Image not available")
            
            with col2:
                st.write("**Location:** ", fort.get('details', {}).get('Location', 'N/A'))
                st.write("**Type:** ", fort.get('details', {}).get('Type', 'N/A'))
                st.write("**Built:** ", fort.get('details', {}).get('Built', 'N/A'))
                st.write("**Condition:** ", fort.get('details', {}).get('Condition', 'N/A'))
                
                if fort.get('details', {}).get('Coordinates'):
                    st.write("**Coordinates:** ", fort['details']['Coordinates'])

def show_cultural_insights():
    st.header("Cultural Insights")
    
    # Connect to Snowflake
    conn = init_snowflake_connection()
    if conn:
        try:
            # Example query - replace with your actual query
            query = "SELECT * FROM cultural_insights LIMIT 10"
            df = pd.read_sql(query, conn)
            
            # Display insights
            st.subheader("Cultural Heritage Statistics")
            st.dataframe(df)
            
            # Add visualizations
            if not df.empty:
                fig = px.bar(df, x='category', y='count', title='Cultural Heritage Distribution')
                st.plotly_chart(fig)
                
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
            query = "SELECT * FROM tourism_data LIMIT 10"
            df = pd.read_sql(query, conn)
            
            # Display tourism data
            st.subheader("Tourism Statistics")
            st.dataframe(df)
            
            # Add visualizations
            if not df.empty:
                fig = px.line(df, x='date', y='visitors', title='Tourist Visits Over Time')
                st.plotly_chart(fig)
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            conn.close()
    else:
        st.warning("Please configure Snowflake credentials to view tourism data.")

if __name__ == "__main__":
    main() 