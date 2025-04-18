def remove_blank_rows(df, column_name="phoneUnformatted"):
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