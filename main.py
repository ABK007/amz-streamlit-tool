import streamlit as st
import pandas as pd
from st_components import st_select_multiple_files
from functions import remove_blank_rows


st.title("Creating CSV file for WhatsApp Business API")

# This function will create a file uploader widget that accepts 
# multiple CSV files and previews them and returns combined dataframe.
df = st_select_multiple_files() 

st.markdown("---") # Add a separator line

if df is None:
    st.warning("Select at least one .csv file to upload")

else:
    st.write(f"Total rows in combined CSV: {df.shape[0]}")
    st.write(f"Total columns in combined CSV: {df.shape[1]}")
    st.write("### Combined CSV files preview")
    
    df = remove_blank_rows(df, column_name="(Child) ASIN") # removing blank rows from the specified column
    df = df.drop_duplicates() # removing duplicates
    
    st.dataframe(df, height=600)
    
    st.write("### Output CSV Column Selection")


    # Let users select which columns to include in the output CSV.
    selected_columns = st.multiselect(
        "Select columns to include:",
        options=df.columns.tolist(),
        default=["(Child) ASIN", "Title", "Sessions - Total"]
    )

    # For each selected column, allow the user to input a desired output name.
    st.write("### Column Mapping")
    mapping = {}
    for col in selected_columns:
        new_name = st.text_input(f"Output column name for '{col}'", value=col)
        mapping[col] = new_name

    # Show a preview of the DataFrame with renamed columns.
    
    st.write("### Adding Tags column")
    tag_value = st.text_input("Tag Column Value")
    if selected_columns:
        # Rename only the selected columns, leave the others unchanged if they are not selected.
        df_subset = df[selected_columns].rename(columns=mapping)
