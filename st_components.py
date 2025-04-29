import streamlit as st
import pandas as pd
import os

from functions import extract_date_from_filename

def st_select_multiple_files_(date=False, unique_key=None):
    """ create a file uploader widget that accepts multiple spreadsheet files and returns combined dataframe.
    paratmeters:
        date: bool, if True, it will extract the date from the filename and add it to the dataframe.
        
    returns:
        combined_df: pd.DataFrame, the combined dataframe of all uploaded files."""
        
        
    uploaded_files = st.sidebar.file_uploader(
        "Choose a spreadsheet file:", type=["xlsx", "xls", "csv"], accept_multiple_files=True,
        key=unique_key,  # Unique key for the file uploader
    )
    
    df_list = []  # List to hold dataframes for each uploaded file
    combined_df = pd.DataFrame()  # Initialize an empty dataframe for combined data
    df = pd.DataFrame()  # Initialize an empty dataframe for dataframe

    for uploaded_file in uploaded_files: 
        filename = uploaded_file.name
        name_lower = filename.lower()
        
        try:
            if name_lower.endswith('.csv'):
                # Process each file; assuming it's a CSV file
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            # Process each file; assuming it's a CSV file
            
            elif name_lower.endswith('.xlsx') or name_lower.endswith('.xls'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                
            else:
                st.error("Unsupported file type. Please provide a .csv, .xlsx or .xls file.")
            
            if date: # extract the date from the filename
                df['date'] = extract_date_from_filename(name_lower)
            
            st.write(f"#### Uploaded file preview: {uploaded_file.name}")
            st.dataframe(df.head())
            
            # add and combine the dataframes to the list
            df_list.append(df)
            
            combined_df = pd.concat(df_list, ignore_index=True)
            
        except Exception as e:
            st.error(f"following error occurred: {e}")
            
    return combined_df