.##
##   Packages Used
##

import pandas as pd
import gdown
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import numpy as np
from scipy.spatial import distance
from numpy.linalg import LinAlgError
from IPython.display import HTML
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
##
##   Data Upload
##

file_id = '1JjYmvA8qTPOh_dVAVkvsapP-xtes7F4h'
url = f'https://drive.google.com/uc?id={file_id}'
output = 'spotify_songs.csv'
gdown.download(url, output, quiet=False)

songs = pd.read_csv('spotify_songs.csv')

##
##   Data Preprocessing
##

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


def preprocesse_songs(df):
    df.drop(columns=['playlist_name', 'playlist_id'], inplace=True)
    df.drop_duplicates(subset=['track_name','track_artist'], inplace=True)
    df = df[(df.duration_ms > df.duration_ms.quantile(0.01))]
    df.dropna(inplace=True)
    df['track_album_release_date'] = standardize_date(df['track_album_release_date'])
    df['release_year']  = df['track_album_release_date'].dt.year
    df = df.drop(columns=['track_album_release_date'])
    encoder = LabelEncoder()
    df['track_artist_label'] = encoder.fit_transform(df['track_artist'])
    df['track_album_id_label'] = encoder.fit_transform(df['track_album_id'])
    df['artist_track'] = df.apply(lambda x: f"{x['track_artist']} - {x['track_name']}", axis=1)
 
    return df

songs = preprocesse_songs(songs)


##
##   Clustering Process
##

clustering_data =  songs[['danceability', 'energy', 'key', 'loudness', 'mode',
       'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo','release_year']]

pca = PCA(n_components=2)
scaled_data = pca.fit_transform(clustering_data)

kmeans = KMeans(n_clusters=4, random_state=42)
songs.loc[:, 'kmeans_labels'] = kmeans.fit_predict(scaled_data)
clustering_data.loc[:, 'kmeans_labels'] = kmeans.fit_predict(scaled_data)

clustering_data = clustering_data.drop(columns='release_year')


##
##   Prediction Process
##

## User Input - These should pprobably be drop down menus using the artist_track column as options and a few options of how many songs
## the user would like to be recommended as the output (e.g.: 10, 20, or 30)
song_name = input('Input the songs artist and song name as "Artist - Track":\n')
# Should we have a max here? 100 maybe?
top_n = int(input('How many songs would you like to be recommended?\n'))


user_input = songs[(songs.artist_track==song_name)]

num_user_input = clustering_data.loc[user_input.index]


like_songs = clustering_data[(clustering_data.kmeans_labels.values==num_user_input.kmeans_labels.values)]
like_songs = like_songs.drop(index=user_input.index)


# Calculate the covariance matrix
cov_matrix = np.cov(like_songs, rowvar=False)

try:
    # Inverse of the covariance matrix
    inv_cov_matrix = np.linalg.inv(cov_matrix)
except LinAlgError:
    # If the covariance matrix is singular (which means it's not inversible), compute the pseudoinverse
    inv_cov_matrix = np.linalg.pinv(cov_matrix)

# Function to find the "top_n" most similar songs using Mahalanobis distance
def find_top_similar_songs(songs_df, user_song, inv_cov_matrix, top_n=top_n):
    user_song = np.array(user_song.values.flatten())
    

    distances = {}
    for idx, song_features in songs_df.iterrows():
        song_features = np.array(song_features.values.flatten())
        # Calculate Mahalanobis distance between user song and current song
        distances[idx] = distance.mahalanobis(user_song, song_features, inv_cov_matrix)
    
    # Top N most similar songs by distance
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    top_similar_indices = [idx for idx, _ in sorted_distances[:top_n]]
    
    top_songs = songs_df.loc[top_similar_indices]
    top_distances = [distances[idx] for idx in top_similar_indices]
    
    return top_songs, top_distances


top_songs, top_distances = find_top_similar_songs(like_songs, num_user_input, inv_cov_matrix, top_n=top_n)
recommended_tracks = songs[(songs.index.isin(top_songs.index))][['track_name','track_artist','track_album_name']]

print(recommended_tracks)

recommended_tracks = HTML(recommended_tracks.to_html(index=False))
