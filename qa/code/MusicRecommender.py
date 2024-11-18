import pandas as pd
import numpy as np
import gdown
import json
import sys
import os
import pickle
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 20)
from sklearn.preprocessing import LabelEncoder
from scipy.spatial import distance
from numpy.linalg import LinAlgError
from helper import *
import streamlit as st



class MusicRecommender:
    def __init__(self):
        self.config = self.load_config()
        self.songs = self.read_data()

        # Importing pre-trained models
        with open('../models/mood_gb_model.pkl', 'rb') as file:
            self.mood_gb_model = pickle.load(file)
        with open('../models/mood_encoder_model.pkl', 'rb') as file:
            self.mood_encoder_model = pickle.load(file)
        with open('../models/kmeans_model.pkl', 'rb') as file:
            self.kmeans_model = pickle.load(file)

        # Preprocess data 
        self.preprocessed_songs = self.preprocess_songs()

    def load_config(self):
        with open('../config/config.json', 'r') as f:
            config = json.load(f)
        return config

    def read_data(self):
        # Access the values from the loaded JSON
        file_id = self.config['file_id']
        url = self.config['url'].replace("file_id", file_id)  # Replace "file_id" in the URL
        output_path = self.config['output_path']
        output_file = self.config['output_file']
        data_loc = os.path.join(output_path, output_file)

        # Try loading the data, otherwise download and save
        try:
            songs = pd.read_csv(data_loc)
            print("Loading data from local repository...")
            print("Data loaded! \n")
        except:
            print("Downloading data from cloud...")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            gdown.download(url, data_loc, quiet=True)
            print("Reading data...")
            songs = pd.read_csv(data_loc)
            print("Data loaded! \n")

        return songs
    
    def mood_prediction(self, df):
        # Load input features    
        model_input_features = self.config['gb_input_features']

        # Predict mood
        df['mood_numeric'] = self.mood_gb_model.predict(df[model_input_features])
        df['mood'] = self.mood_encoder_model.inverse_transform(df['mood_numeric'])

        return df['mood']
    
    def kmeans_prediction(self, df):
        # Load input features    
        kmeans_input_features = self.config['kmeans_input_features']

        # Predict mood
        df['kmeans_labels'] = self.kmeans_model.predict(df[kmeans_input_features])

        return df['kmeans_labels']
        

    def preprocess_songs(self):
        print("Preprocessing the data..")
        df = self.songs
        df.drop(columns=['playlist_name', 'playlist_id'], inplace=True)
        df.drop_duplicates(subset=['track_name','track_artist'], inplace=True)
        df = df[(df.duration_ms > df.duration_ms.quantile(0.01))]
        df.dropna(inplace=True)
        df['track_album_release_date'] = standardize_date(df['track_album_release_date'])
        df['release_year'] = df['track_album_release_date'].dt.year
        df = df.drop(columns=['track_album_release_date'])
        encoder = LabelEncoder()
        df['track_artist_label'] = encoder.fit_transform(df['track_artist'])
        df['track_album_id_label'] = encoder.fit_transform(df['track_album_id'])
        df['artist_track'] = df.apply(lambda x: f"{x['track_artist']} - {x['track_name']}", axis=1)

        # Predictions
        df['mood'] = self.mood_prediction(df)
        df['kmeans_labels'] = self.kmeans_prediction(df)  
        print("Preprocessing completed! \n")   
        return df   


    def recommend_by_mood(self, mood, top_n=10):
        top_n = int(top_n)
        songs = self.preprocessed_songs
        mood_musics = songs[songs['mood'] == mood].sort_values(by=['track_popularity'], ascending=False).head(300)
        # mood_musics = mood_musics[['track_id', 'track_name', 'track_artist', 'track_popularity', 
        #                            'playlist_genre', 'playlist_subgenre', 'release_year', 'mood']]

        sampled_musics = mood_musics.groupby('release_year').apply(
            lambda x: x.sample(min(len(x), max(1, top_n // len(mood_musics['release_year'].unique()))))
        ).reset_index(drop=True)

        if len(sampled_musics) < top_n:
            additional_songs = mood_musics.drop(sampled_musics.index).sample(top_n - len(sampled_musics))
            sampled_musics = pd.concat([sampled_musics, additional_songs])

        # Format output
        recommended_tracks = output_format(sampled_musics, top_n)

        return recommended_tracks

    def recommend_similar_songs(self, song_name, top_n=10):
        top_n = int(top_n)
        kmeans_input_features = self.config['kmeans_input_features']
        songs = self.preprocessed_songs
        clustering_data = songs[kmeans_input_features + ["kmeans_labels"]]

        # User input and feature extraction
        user_input = songs[songs['track_name'] == song_name]
        if user_input.empty:
            print("Song not found in the dataset.")
            return None

        # Extract features for the user's selected song using the same features as clustering_data
        num_user_input = clustering_data.loc[user_input.index]
        if num_user_input.empty:
            print("User input features not found in clustering data.")
            return None

        # Convert num_user_input to a single row vector
        user_song = num_user_input.iloc[0][kmeans_input_features].values

        # Filter songs with the same kmeans label, then drop the user's song index
        like_songs = clustering_data[
            clustering_data['kmeans_labels'] == num_user_input['kmeans_labels'].values[0]
        ]

        # Check if the user's song index exists in like_songs and drop it if it does
        common_indexes = like_songs.index.intersection(user_input.index)
        like_songs = like_songs.drop(index=common_indexes)

        # Ensure there are enough songs for the analysis
        if like_songs.empty or len(like_songs) < 20:
            print("Not enough similar songs found to make a recommendation.")
            return None

        # Calculate covariance matrix
        cov_matrix = np.cov(like_songs[kmeans_input_features].values, rowvar=False)
        try:
            inv_cov_matrix = np.linalg.inv(cov_matrix)
        except LinAlgError:
            inv_cov_matrix = np.linalg.pinv(cov_matrix)

        # Find top N similar songs using Mahalanobis distance
        def find_top_similar_songs(songs_df, user_song, inv_cov_matrix, top_n):
            distances = {}
            for idx, song_features in songs_df.iterrows():
                song_features = np.array(song_features[kmeans_input_features].values.flatten())
                distances[idx] = distance.mahalanobis(user_song, song_features, inv_cov_matrix)

            # Sort distances and get the top N indices
            sorted_distances = sorted(distances.items(), key=lambda x: x[1])
            top_similar_indices = [idx for idx, _ in sorted_distances[:top_n]]

            top_songs = songs_df.loc[top_similar_indices]
            return top_songs

        top_songs = find_top_similar_songs(like_songs, user_song, inv_cov_matrix, top_n=top_n)
        if top_songs.empty:
            print("No similar songs found.")
            return None

        # Select Musics
        recommended_tracks = songs[songs.index.isin(top_songs.index)]

        # Format output
        recommended_tracks = output_format(recommended_tracks, top_n)
        return recommended_tracks