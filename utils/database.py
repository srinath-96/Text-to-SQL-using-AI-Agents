import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text, inspect
import io
import streamlit as st

def create_database_from_upload(uploaded_file, db_name="data.db", table_name="data"):
    """
    Create a SQLite database from an uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        db_name: Name of the database file
        table_name: Name of the table to create
        
    Returns:
        DataFrame: The uploaded data
    """
    try:
        # Determine file type and read accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        
        # Create SQLite database
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Error creating database: {e}")
        return None

def get_database_engine(db_name="data.db"):
    """
    Get SQLAlchemy engine for the database
    
    Args:
        db_name: Name of the database file
        
    Returns:
        SQLAlchemy engine
    """
    return create_engine(f"sqlite:///{db_name}")

def get_schema_description(engine):
    """
    Get a description of the database schema
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        str: Description of tables and their columns
    """
    inspector = inspect(engine)
    schema_description = ""
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema_description += f"Table '{table_name}':\n"
        schema_description += "\n".join(f" - {col['name']}: {col['type']}" for col in columns) + "\n"
    
    return schema_description.strip()
