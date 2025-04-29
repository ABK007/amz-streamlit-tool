import pandas as pd
import os

def remove_blank_rows(df: pd.DataFrame, column_name: str="phoneUnformatted") -> pd.DataFrame:
    """
    Remove the rows in dataframe with empty values or empty strings
    
    Parameters:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the phone column to convert (default "phone_unformatted").
        
    Returns:
        dataframe with removed empty values rom the specified column.
        
    """
    df_clean = df.dropna(subset=[column_name])    # Remove NaN values first
    df_clean = df_clean[df_clean[column_name] != ''] # Remove empty strings next
    
    return df_clean


def read_data_file(file_path: str) -> pd.DataFrame:
    """
    Read an excel file (.csv, .xlsx, .xls) and return a DataFrame.
    
    Parameters:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV file.
        
    """
    # checking the data file type
    file_extension = os.path.splitext(file_path)[1].lower()
    print(file_extension)
    if file_extension == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
        
    else:
        raise ValueError("Unsupported file type. Please provide a .csv, .xlsx or .xls file.")        
    
    
    return df


def extract_date_from_filename(file_name: str) -> pd.Timestamp:
    """
    Extract date from the filename and convert it to a pandas datetime object.
    
    Parameters:
        file_name (str): The name of the file.
        
    Returns:
        pd.Timestamp: The extracted date as a pandas datetime object.
        
    """
    # Extract the date string from the filename (assuming it's in the format YYYY-MM-DD)
    file_name_str = os.path.splitext(file_name)[0]
    
    date_str = file_name_str.split('_')[0]  # Assuming the date is the first part of the filename
    
    # Parse the date string into a pandas datetime object
    ts = pd.to_datetime(date_str, infer_datetime_format=True)
    
    return ts.date()