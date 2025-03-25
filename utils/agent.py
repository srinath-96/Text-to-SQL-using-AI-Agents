# utils/agent.py
import os
import re
import json
import ast
from smolagents import tool, CodeAgent, LiteLLMModel
from sqlalchemy import text
import pandas as pd
from utils.database import get_database_engine, get_schema_description
from utils.visualization import visualize_data

def setup_agent():
    """
    Set up the SmolAgents CodeAgent with the necessary tools and model.
    
    Returns:
        CodeAgent: Configured agent
    """
    # Set up API key for Gemini
    os.environ["GEMINI_API_KEY"] = 'API_KEY'
    
    # Initialize the model
    model = LiteLLMModel(model_id='gemini/gemini-2.0-flash')
    
    # Create the agent with tools
    agent = CodeAgent(
        tools=[sql_engine, describe_schema, visualize_data_tool],
        model=model
    )
    
    return agent

@tool
def sql_engine(query: str) -> str:
    """
    Executes SQL queries on the database and returns results.
    
    Args:
        query: The SQL query to execute
    
    Returns:
        str: Query results as a formatted string or DataFrame JSON
    """
    try:
        engine = get_database_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            
            if not rows:
                return "Query executed successfully, but no data returned."
            
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(rows, columns=columns)
            return df.to_json(orient="records")
    except Exception as e:
        return f"Error: {e}"

@tool
def describe_schema() -> str:
    """
    Provides a description of the database schema.
    
    Returns:
        str: Description of tables and their columns
    """
    engine = get_database_engine()
    return get_schema_description(engine)

@tool
def visualize_data_tool(data_json: str, chart_type: str = "auto", title: str = "", x_col: str = None, y_col: str = None) -> str:
    """
    Creates visualizations based on the data.
    
    Args:
        data_json: JSON string of data to visualize
        chart_type: Type of chart to create (bar, line, scatter, pie, histogram, auto)
        title: Chart title to display
        x_col: Column name to use for x-axis
        y_col: Column name to use for y-axis
    
    Returns:
        str: Path to the saved visualization file
    """
    file_path = visualize_data(data_json, chart_type, title, x_col, y_col)
    if file_path:
        return f"Visualization saved to {file_path}"
    else:
        return "Failed to create visualization"

def run_dashboard_query(user_input, agent):
    """
    Process a natural language query using the agent
    
    Args:
        user_input: User's natural language query
        agent: Configured SmolAgents agent
        
    Returns:
        dict: Components of the response including SQL query, data summary, etc.
    """
    # Construct the prompt
    prompt = f"""
    I need you to process this natural language query: "{user_input}"
    
    Please follow these steps one by one:
    
    1. First, examine the database schema using describe_schema() to understand the available data.
    
    2. Next, convert the query to SQL and execute it using sql_engine().
    
    3. Then, analyze the results and provide a brief data summary.
    
    4. Finally, create an appropriate visualization using visualize_data() with the results.
    
    Your final response should include:
    
    - The SQL query you created
    - A summary of the data findings
    - The type of chart you created (bar, pie, line, etc.)
    - The path to the visualization file
    
    Format your response with clear section headers for each component.
    """
    
    # Run the agent with the prompt
    response = agent.run(prompt)
    
    # Extract components using string parsing
    extracted_components = {}
    
    # Convert response to string if it's not already
    response_text = str(response)
    
    # Try to parse the dictionary-like structure
    try:
        # Check if the whole response looks like a dictionary
        if '{' in response_text and '}' in response_text:
            # Extract the dictionary-like part
            dict_pattern = r'\{[^{}]*\}'
            dict_match = re.search(dict_pattern, response_text)
            if dict_match:
                dict_text = dict_match.group(0)
                # Fix single quotes and replace with double quotes for JSON parsing
                fixed_dict_text = dict_text.replace("'", '"')
                try:
                    # Try parsing as JSON
                    dict_data = json.loads(fixed_dict_text)
                    # Map standard keys
                    key_mappings = {
                        'sql_query': ['sql_query', 'SQL Query', 'query', 'sql'],
                        'data_summary': ['data_summary', 'Data Summary', 'summary', 'findings'],
                        'visualization_type': ['visualization_type', 'Chart Type', 'chart_type', 'type'],
                        'visualization': ['visualization', 'Visualization File', 'visualization_file', 'file', 'path']
                    }
                    
                    for our_key, possible_keys in key_mappings.items():
                        for possible_key in possible_keys:
                            if possible_key in dict_data:
                                extracted_components[our_key] = dict_data[possible_key]
                                break
                except json.JSONDecodeError:
                    # If JSON parsing fails, try using ast.literal_eval
                    try:
                        dict_data = ast.literal_eval(dict_text)
                        # Map keys as before
                        key_mappings = {
                            'sql_query': ['sql_query', 'SQL Query', 'query', 'sql'],
                            'data_summary': ['data_summary', 'Data Summary', 'summary', 'findings'],
                            'visualization_type': ['visualization_type', 'Chart Type', 'chart_type', 'type'],
                            'visualization': ['visualization', 'Visualization File', 'visualization_file', 'file', 'path']
                        }
                        
                        for our_key, possible_keys in key_mappings.items():
                            for possible_key in possible_keys:
                                if possible_key in dict_data:
                                    extracted_components[our_key] = dict_data[possible_key]
                                    break
                    except (ValueError, SyntaxError):
                        # If ast.literal_eval fails, do manual extraction
                        # For SQL query
                        sql_match = re.search(r"['\"]?SQL Query['\"]?\s*:\s*['\"](.+?)['\"]", dict_text)
                        if sql_match:
                            extracted_components['sql_query'] = sql_match.group(1)
                        
                        # For Data Summary
                        summary_match = re.search(r"['\"]?Data Summary['\"]?\s*:\s*['\"](.+?)['\"]", dict_text)
                        if summary_match:
                            extracted_components['data_summary'] = summary_match.group(1)
                        
                        # For Visualization Type
                        type_match = re.search(r"['\"]?Chart Type['\"]?\s*:\s*['\"](.+?)['\"]", dict_text)
                        if type_match:
                            extracted_components['visualization_type'] = type_match.group(1)
                        
                        # For Visualization File
                        file_match = re.search(r"['\"]?Visualization File['\"]?\s*:\s*['\"](.+?)['\"]", dict_text)
                        if file_match:
                            extracted_components['visualization'] = file_match.group(1)
    except Exception as e:
        print(f"Error parsing response: {e}")
    
    # If we still don't have all components, fallback to basic regex pattern matching on the full text
    if len(extracted_components) < 4:
        # SQL Query - look for SQL-like patterns
        if 'sql_query' not in extracted_components:
            sql_patterns = [
                r"SQL Query:\s*(.+?)(?=\n|$)",
                r"SELECT(.+?)(?=\n|$)",
                r"COUNT\(\*\)(.+?)(?=\n|$)"
            ]
            
            for pattern in sql_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    extracted_components['sql_query'] = match.group(1).strip()
                    break
        
        # Data Summary
        if 'data_summary' not in extracted_components:
            summary_patterns = [
                r"Data Summary:\s*(.+?)(?=\n|$)",
                r"dataset contains(.+?)(?=\n|$)",
                r"total of(.+?)records",
            ]
            
            for pattern in summary_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    extracted_components['data_summary'] = match.group(1).strip()
                    break
        
        # Visualization Type
        if 'visualization_type' not in extracted_components:
            # Check if 'bar' is in the response
            if 'bar' in response_text.lower():
                extracted_components['visualization_type'] = 'bar'
            elif 'line' in response_text.lower():
                extracted_components['visualization_type'] = 'line'
            elif 'scatter' in response_text.lower():
                extracted_components['visualization_type'] = 'scatter'
            elif 'pie' in response_text.lower():
                extracted_components['visualization_type'] = 'pie'
            elif 'histogram' in response_text.lower():
                extracted_components['visualization_type'] = 'histogram'
            else:
                extracted_components['visualization_type'] = 'auto'
        
        # Visualization File
        if 'visualization' not in extracted_components:
            viz_pattern = r"viz_\d+\.png"
            viz_match = re.search(viz_pattern, response_text)
            if viz_match:
                extracted_components['visualization'] = viz_match.group(0)
    
    return extracted_components
