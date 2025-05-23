# Indian Cultural Heritage Explorer

A Streamlit application that showcases India's rich cultural heritage through historical forts and promotes responsible tourism.

## Features

- Interactive exploration of historical forts across India
- Filter forts by state and type
- View detailed information and images of each fort
- Cultural insights through Snowflake integration
- Tourism data analysis and visualization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Snowflake credentials in `.env` file:
```
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

3. Run the application:
```bash
streamlit run app.py
```

## Data Sources

- `indian_forts.json`: Contains detailed information about historical forts in India
- Snowflake database: Stores cultural insights and tourism data

## Project Structure

- `app.py`: Main Streamlit application
- `requirements.txt`: Python dependencies
- `.env`: Snowflake credentials (not tracked in git)
- `indian_forts.json`: Fort data in JSON format

## Technologies Used

- Streamlit
- Python
- Snowflake
- Plotly
- Pandas
- Pillow

## Contributing

Feel free to submit issues and enhancement requests!
