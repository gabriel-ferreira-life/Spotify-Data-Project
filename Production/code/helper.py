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


def search_songs(songs_df, partial_name, max_results=100):
    """
    Searches for songs with names that partially match the given input.
    
    Parameters:
        songs_df (DataFrame): The DataFrame containing song information.
        partial_name (str): The partial name of the song to search for.
        max_results (int): The maximum number of results to return.
    
    Returns:
        DataFrame: A DataFrame with matching song names and artists.
    """
    matching_songs = songs_df[songs_df['track_name'].str.contains(partial_name, case=False, na=False)]
    return matching_songs[['track_name', 'track_artist']].drop_duplicates().head(max_results)

def search_artist(songs_df, partial_artist, max_results=100):
    """
    Searches for artists with names that partially match the given input.
    
    Parameters:
        songs_df (DataFrame): The DataFrame containing song information.
        partial_artist (str): The partial name of the artist to search for.
        max_results (int): The maximum number of results to return.
    
    Returns:
        DataFrame: A DataFrame with matching artist names.
    """
    matching_artists = songs_df[songs_df['track_artist'].str.contains(partial_artist, case=False, na=False)]
    return matching_artists[['track_artist']].drop_duplicates().head(max_results)

def output_format(recommendations_df, top_n):
    recommendations_df = recommendations_df[['track_id', 'track_name','track_artist','track_album_name']]
    recommendations_df.columns = ["Song ID", "Song Name", "Artist Name", "Album Name"]
    recommendations_df = recommendations_df.sample(top_n).reset_index(drop=True)
    recommendations_df.index = recommendations_df.index + 1
    return recommendations_df