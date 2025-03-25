import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import json

def visualize_data(data_json, chart_type="auto", title="", x_col=None, y_col=None):
    """
    Creates visualizations based on the data.
    
    Args:
        data_json: JSON string of data to visualize.
        chart_type: Type of chart to create (bar, line, scatter, pie, histogram, auto).
        title: Chart title to display.
        x_col: Column name to use for x-axis.
        y_col: Column name to use for y-axis.
        
    Returns:
        str: Path to the saved visualization file
    """
    try:
        # Convert JSON to DataFrame
        df = pd.read_json(data_json)
        
        if df.empty:
            return None
        
        # Auto-detect columns if not specified
        if not x_col:
            # Try to find a categorical or datetime column for x
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if not categorical_cols.empty:
                x_col = categorical_cols[0]
            else:
                x_col = df.columns[0]
        
        if not y_col:
            # Try to find a numerical column for y
            numerical_cols = df.select_dtypes(include=['number']).columns
            if not numerical_cols.empty:
                y_col = numerical_cols[0]
            elif len(df.columns) > 1:
                y_col = df.columns[1]
            else:
                y_col = df.columns[0]
        
        # Auto-detect chart type if set to auto
        if chart_type == "auto":
            if df[x_col].nunique() <= 10 and pd.api.types.is_numeric_dtype(df[y_col]):
                chart_type = "bar"
            elif pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                chart_type = "scatter"
            elif df[x_col].nunique() > 10 and pd.api.types.is_numeric_dtype(df[y_col]):
                chart_type = "line"
            else:
                chart_type = "bar"
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create visualization based on chart type
        if chart_type == "bar":
            sns.barplot(x=x_col, y=y_col, data=df)
        elif chart_type == "line":
            sns.lineplot(x=x_col, y=y_col, data=df)
        elif chart_type == "scatter":
            sns.scatterplot(x=x_col, y=y_col, data=df)
        elif chart_type == "pie" and len(df) <= 10:
            plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')
        elif chart_type == "histogram" and pd.api.types.is_numeric_dtype(df[x_col]):
            sns.histplot(df[x_col])
        else:
            sns.barplot(x=x_col, y=y_col, data=df)
        
        plt.title(title if title else f"{y_col} by {x_col}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        file_name = f"viz_{int(time.time())}.png"
        plt.savefig(file_name)
        plt.close()
        
        return file_name
    
    except Exception as e:
        print(f"Visualization error: {e}")
        return None
