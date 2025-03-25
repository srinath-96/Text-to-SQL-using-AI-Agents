Text2SQL Visualization Dashboard
================================

A Streamlit application that converts natural language queries to SQL and visualizes the results from your data.

Overview
--------

This dashboard allows users to:

-   Upload CSV or Excel files

-   Query the data using natural language

-   View the SQL translation of their queries

-   See data summaries and visualizations

-   Track query history for easy reuse

Features
--------

-   Natural Language to SQL: Ask questions about your data in plain English

-   Automatic Visualization: Generates appropriate charts based on query results

-   Interactive Interface: User-friendly Streamlit interface

-   Query History: Saves previous queries for quick access

-   Schema Inspection: View the database schema to understand available data

Installation
------------

1.  Clone this repository:

bash

`git clone https://github.com/yourusername/text2sql-viz-streamlit.git cd text2sql-viz-streamlit `

1.  Create a virtual environment and activate it:

bash

`python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate  `

1.  Install the required packages:

bash

`pip install -r requirements.txt `

Usage
-----

1.  Start the Streamlit application:

bash

`streamlit run app.py `

1.  Open your web browser and navigate to the URL shown in the terminal (typically [http://localhost:8501](http://localhost:8501/))

2.  Upload your data file (CSV or Excel)

3.  Enter natural language queries about your data

4.  Explore the visualizations and SQL translations

Example Queries
---------------

-   "Show me sales by region"

-   "What is the average age by gender?"

-   "Count customers by product category"

-   "Which department has the highest salary?"

-   "Show the trend of sales over time"

Project Structure
-----------------

text

`text2sql_viz_streamlit/ ├── app.py                # Main Streamlit application ├── requirements.txt      # Dependencies ├── utils/ │   ├── __init__.py       # Package initialization │   ├── database.py       # Database operations │   ├── visualization.py  # Visualization functions │   └── agent.py          # SmolAgents setup and query processing `

Dependencies
------------

-   streamlit: Web application framework

-   pandas: Data manipulation

-   matplotlib & seaborn: Visualization

-   sqlalchemy: Database operations

-   smolagents: Natural language processing

-   sqlite3: Database engine

Configuration
-------------

The application uses the Gemini API for natural language processing. You can change the API key in the `utils/agent.py` file:

python

`os.environ["GEMINI_API_KEY"]  =  'YOUR_API_KEY'  `

Limitations
-----------

-   The application works best with structured, tabular data

-   Complex queries might require refinement
