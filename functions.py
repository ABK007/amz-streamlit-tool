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