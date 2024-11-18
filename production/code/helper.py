import pandas as pd
def standardize_date(dates):
    """
    Standardizes a list of date strings to the format 'YYYY-MM-DD'.

    Parameters:
        dates (iterable): An iterable containing date strings in various formats
                          ('YYYY', 'YYYY-MM', 'YYYY-MM-DD').

    Returns:
        pd.Series: A Pandas Series with dates converted to datetime format, where:
                   - 'YYYY' is converted to 'YYYY-01-01'
                   - 'YYYY-MM' is converted to 'YYYY-MM-01'
                   - 'YYYY-MM-DD' remains unchanged
                   Invalid dates will be set as NaT (Not a Time).
    """
    standardized_dates = []
    for date in dates:
        if pd.isna(date):
            standardized_dates.append(date)
        elif len(date) == 4:
            standardized_dates.append(f"{date}-01-01")
        elif len(date) == 7:
            standardized_dates.append(f"{date}-01")
        else:
            standardized_dates.append(date)

    return pd.to_datetime(standardized_dates, errors='coerce')