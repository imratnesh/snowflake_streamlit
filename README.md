# Indian Cultural Heritage Explorer

A Streamlit application that explores Indian forts and tourism data, providing insights into cultural heritage and tourist visits across different states.

## Features

### Forts Explorer
- Interactive exploration of historical forts across India
- Filter forts by state and type
- View detailed information including:
  - Location and coordinates
  - Historical details
  - Images
  - Tourism statistics for the state

### Cultural Insights
- Analysis of foreign tourist visits by state
- Interactive visualizations:
  - Bar charts showing tourist visits
  - Pie charts for distribution analysis
  - Key statistics and metrics

### Tourism Data
- Year-wise analysis of tourist visits
- Country-wise visitor statistics
- Interactive visualizations:
  - Line plots for trend analysis
  - Bar charts for top countries
  - Year-over-year growth analysis

## Prerequisites

- Python 3.7+
- Snowflake account with appropriate credentials
- Required Python packages (see requirements.txt)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/imratnesh/snowflake_streamlit.git
cd snowflake_streamlit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Snowflake credentials:
```
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Data Sources

- Forts data: Historical information about Indian forts
- Tourism data: Foreign tourist visits by state and country
- All data is stored in Snowflake database

## Project Structure

```
snowflake_streamlit/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── README.md          # This file
├── tour/              # Tourism data directory
└── indian_forts.json  # Forts data file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data provided by HackerEarth and YourStory
- Built with Streamlit
- Powered by Snowflake
