import streamlit as st
import pandas as pd
from st_components import st_select_multiple_files_
from functions import remove_blank_rows, processing_catalog_file
from charts import creating_sessions_chart


# setting upp page config
st.set_page_config(
    page_title="My App",
    layout="wide",  # ← this makes the page full‑width
    initial_sidebar_state="auto",  # optional: expanded/collapsed sidebar
)


st.title("Amazon Analytics Tool")
st.sidebar.title("Upload Files Here")

# This function will create a file uploader widget that accepts
# multiple CSV files and previews them and returns combined dataframe.
st.sidebar.write("## Upload Sessions Files here")
df = st_select_multiple_files_(date=True, unique_key="session")

st.sidebar.write("## Upload PPC Files here")
ppc_df = st_select_multiple_files_(date=False, unique_key="ppc")


st.markdown("---")  # Add a separator line


st.write("### Combined dataframe of sessions + PPC data")
st.write("> Removed blank rows and duplicates from the combined CSV files")

df = remove_blank_rows(
    df, column_name="(Child) ASIN"
)  # removing blank rows from the specified column
df = df.drop_duplicates()  # removing duplicates

# -------------------------------------------------------------
# adding sku and tags to the dataframe from catalog file

# adding a new dataframe caontaining SKU names and tags for each ASIN
sku_lookup = processing_catalog_file(mapping_column="SKU")

# create the new column by looking up every (Child) ASIN
df["SKU"] = df["(Child) ASIN"].map(sku_lookup)

tag_lookup = processing_catalog_file(mapping_column="Category")

# create the new column by looking up every (Child) ASIN
df["tag"] = df["(Child) ASIN"].map(tag_lookup)

df["date"] = pd.to_datetime(
    df["date"], errors="coerce"
)  # Convert the 'date' column to datetime format


# --------------------------------------------------------------
# Merging with ppc df

ppc_df["Date"] = pd.to_datetime(
    ppc_df["Date"]
)  # Convert the 'date' column to datetime format
ppc_df["Clicks"] = pd.to_numeric(ppc_df["Clicks"], errors="coerce").fillna(
    0
)  # Convert the 'clicks' column to numeric, replacing non-numeric values with 0

ppc_df = remove_blank_rows(ppc_df, column_name="Advertised SKU")
ppc_df = ppc_df.drop_duplicates()

clicks_by_sku_date = (  # grouping the ppc_df by SKU and date and summing the clicks for having only unique SKU and date combinations
    ppc_df.groupby(["Advertised SKU", "Date"], as_index=False)["Clicks"].sum()
)

df = df.merge(
    clicks_by_sku_date,
    left_on=["SKU", "date"],
    right_on=["Advertised SKU", "Date"],
    how="left",
)

df["Clicks"] = df["Clicks"].fillna(0).astype(int)

st.dataframe(df, height=600)

# ----------------------------------------
# creating new columns for the dataframe
df.rename(
    columns={"Clicks": "total_clicks"}, inplace=True
)  # renaming the clicks column to total_clicks

df["ppc_sessions"] = df[
    "total_clicks"
]  # assuming that the each click is equal to one session

df["organic_sessions"] = (
    df["Sessions - Total"] - df["ppc_sessions"]
)  # assuming that the organic sessions are equal to the total sessions minus the ppc sessions

# -----------------------------
# Creating new dataframe with selected columns and renaming them

st.write("### Output CSV Column Selection")
# Let users select which columns to include in the output CSV.
selected_columns = st.multiselect(
    "Select columns to include:",
    options=df.columns.tolist(),
    default=[
        "(Child) ASIN",
        "SKU",
        "tag",
        "Title",
        "Sessions - Total",
        "date",
        "total_clicks",
        "ppc_sessions",
        "organic_sessions",
    ],
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

    st.write("## Total Sessions by SKU and Date")
    creating_sessions_chart(
        new_df, measure_column= "Sessions - Total", unique_key="total_sessions")
    
    st.write("## Total PPC Sessions by SKU and Date")
    creating_sessions_chart(
        new_df, measure_column= "ppc_sessions", unique_key="ppc_sessions")
    
    
    st.write("## Total Organic Sessions by SKU and Date")
    creating_sessions_chart(
        new_df, measure_column= "organic_sessions", unique_key="organic_sessions")
    
    # creating_plotly_chart(new_df, tag_column="SKU", sku_column="SKU", date_column="date")


else:
    st.warning("Select at least one column to include in the output.")
