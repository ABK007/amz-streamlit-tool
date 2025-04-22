import streamlit as st
import pandas as pd
from st_components import st_select_multiple_files
from functions import remove_blank_rows, read_data_file
from charts import creating_plotly_chart


# setting upp page config
st.set_page_config(
    page_title="My App",
    layout="wide",                # ← this makes the page full‑width
    initial_sidebar_state="auto"  # optional: expanded/collapsed sidebar
)


st.title("Creating CSV file for WhatsApp Business API")

# This function will create a file uploader widget that accepts
# multiple CSV files and previews them and returns combined dataframe.
df = st_select_multiple_files()

st.markdown("---")  # Add a separator line

if df is None:
    st.warning("Select at least one .csv file to upload")

else:
    st.markdown(f"> Total rows in combined CSV: {df.shape[0]}")
    st.markdown(f"> Total columns in combined CSV: {df.shape[1]}")
    st.write("### Combined CSV files preview")
    st.write("> Removed blank rows and duplicates from the combined CSV files")

    df = remove_blank_rows(df, column_name="(Child) ASIN")  # removing blank rows from the specified column
    df = df.drop_duplicates()  # removing duplicates
    
    # adding a new dataframe caontaining SKU names and tags for each ASIN
    df_catalog = read_data_file("spreadsheets\Catalog.xlsx")
    df_catalog = df_catalog.drop_duplicates()
    df_catalog = remove_blank_rows(df_catalog, column_name="ASIN")
    
    
    # build a Series that maps each ASIN to its SKU
    sku_lookup = df_catalog.set_index("ASIN")["SKU"]

    # create the new column by looking up every (Child) ASIN
    df["SKU"] = df["(Child) ASIN"].map(sku_lookup)
    
    # build a Series that maps each ASIN to its SKU
    tag_lookup = df_catalog.set_index("ASIN")["Category"]
    
    # create the new column by looking up every (Child) ASIN
    df["tag"] = df["(Child) ASIN"].map(tag_lookup)
    
    


    st.dataframe(df, height=600)

    st.write("### Output CSV Column Selection")
    # Let users select which columns to include in the output CSV.
    selected_columns = st.multiselect(
        "Select columns to include:",
        options=df.columns.tolist(),
        default=["(Child) ASIN", "Title", "Sessions - Total", "date"],
    )

    st.markdown("---")  # Add a separator line
    
    # For each selected column, allow the user to input a desired output name.
    st.write("### Column Mapping")
    mapping = {}
    for col in selected_columns:
        new_name = st.text_input(f"Output column name for '{col}'", value=col)
        mapping[col] = new_name

    st.markdown("---")  # Add a separator line
    
    st.markdown("### Preview the generated Dataframe")  # Add a separator line
    if selected_columns:
        # Rename only the selected columns, leave the others unchanged if they are not selected.
        new_df = df[selected_columns].rename(columns=mapping)
        
        st.dataframe(new_df, height=600)
        
        file_name = st.text_input("Enter file name to generate .csv file", value="mapped_output.csv")

        # Button to generate CSV
        if st.button("Generate CSV"):
            csv_data = new_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{file_name}",
                mime="text/csv"
            )
            
            
        creating_plotly_chart(new_df)
    else:
        st.warning("Select at least one column to include in the output.")
        
        
    
    
