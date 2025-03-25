import streamlit as st
import pandas as pd
import os
import io
import time
from utils.database import create_database_from_upload, get_database_engine, get_schema_description
from utils.agent import setup_agent, run_dashboard_query
from utils.visualization import visualize_data
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Text2SQL Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Text2SQL Visualization Dashboard")
    
    # Add a sidebar with information
    with st.sidebar:
        st.header("About")
        st.info(
            "This dashboard converts natural language queries to SQL and visualizes the results. "
            "Upload your data and ask questions in plain English!"
        )
        
        st.header("Examples")
        st.markdown(
            """
            Try queries like:
            - Show me sales by region
            - What is the average age by gender?
            - Count customers by product category
            - Which department has the highest salary?
            """
        )
        
        if st.session_state.get('db_created', False):
            st.header("Database Schema")
            if st.button("Show Schema"):
                engine = get_database_engine()
                schema = get_schema_description(engine)
                st.code(schema)
    
    # Session state initialization
    if 'db_created' not in st.session_state:
        st.session_state.db_created = False
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Step 1: File Upload Section
    st.header("Step 1: Upload Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
    
    with col2:
        if st.session_state.db_created:
            st.success("✅ Database created")
            if st.button("Reset Database"):
                st.session_state.db_created = False
                st.session_state.agent = None
                st.session_state.query_history = []
                st.experimental_rerun()
    
    if uploaded_file is not None and not st.session_state.db_created:
        with st.spinner("Creating database..."):
            df = create_database_from_upload(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.session_state.db_created = True
                st.session_state.agent = setup_agent()
                st.success("Database created successfully!")
                st.write("Data Preview:")
                st.dataframe(df.head())
    
    # Step 2: Query Section (only show if database is created)
    if st.session_state.db_created:
        st.header("Step 2: Enter Your Query")
        
        query_text = st.text_area("Enter your natural language query:", 
                                  placeholder="Example: Show me sales by region")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            run_button = st.button("Run Query", type="primary")
        with col2:
            if st.session_state.query_history:
                selected_history = st.selectbox(
                    "Previous queries:", 
                    options=st.session_state.query_history,
                    index=None,
                    placeholder="Select a previous query..."
                )
                if selected_history and selected_history != query_text:
                    query_text = selected_history
                    st.experimental_rerun()
        
        if run_button:
            if query_text:
                # Add to history if not already there
                if query_text not in st.session_state.query_history:
                    st.session_state.query_history.append(query_text)
                
                with st.spinner("Processing your query..."):
                    results = run_dashboard_query(query_text, st.session_state.agent)
                
                # Display results
                if results:
                    st.subheader("Query Results")
                    
                    # Create tabs for different views
                    tab1, tab2, tab3 = st.tabs(["Visualization", "SQL Query", "Data Summary"])
                    
                    with tab1:
                        st.subheader("Visualization")
                        viz_file = results.get('visualization', '')
                        if viz_file and os.path.exists(viz_file):
                            st.image(viz_file)
                            st.caption(f"Chart Type: {results.get('visualization_type', 'Not specified')}")
                        else:
                            st.warning("Visualization not available")
                    
                    with tab2:
                        st.subheader("SQL Query")
                        st.code(results.get('sql_query', 'Query not available'), language="sql")
                    
                    with tab3:
                        st.subheader("Data Summary")
                        st.write(results.get('data_summary', 'Summary not available'))
            else:
                st.warning("Please enter a query first.")
    
    # Footer
    st.markdown("---")
    st.caption("Text2SQL Visualization Dashboard | Built with Streamlit and SmolAgents")

if __name__ == "__main__":
    main()
