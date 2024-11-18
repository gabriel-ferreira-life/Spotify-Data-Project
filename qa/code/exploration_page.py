import streamlit as st
import numpy as np
from helper import standardize_date, search_songs, search_artist
from MusicRecommender import MusicRecommender
import matplotlib.pyplot as plt
from math import pi
from sklearn.preprocessing import StandardScaler

@st.cache_data
def initiate_class():
    return MusicRecommender()

def show_exploration_page():
    # Instantiate the recommender
    recommender = initiate_class()

    # Welcome message
    st.title("Music Exploration")
    st.write("Let's Explore!")

    # Getting preprocessed data
    data = recommender.preprocessed_songs
    pre_model_df = data.drop(columns=['mood_numeric', 'key', 'loudness', 'tempo', 'duration_ms', 'track_popularity', 'release_year', 'mode', 'track_album_id_label', 'track_artist_label', 'kmeans_labels', 'speechiness'])
    numeric_columns = pre_model_df.select_dtypes(include=['number']).columns
        
    # Prepare data
    avg_sensory = pre_model_df[(numeric_columns.tolist() + ['mood'])].groupby('mood').mean()
    categories = avg_sensory.columns

    st.write("""#### Sensory Profile Comparison Across Moods""")
    # Create a figure for the radar chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Define angles for the radar chart
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]

    # Plot each mood on the radar chart
    colors = ['b', 'g', 'r', 'y', 'black'] 
    for i, mood in enumerate(avg_sensory.index):
        values = avg_sensory.loc[mood].tolist()
        values += values[:1]
        
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=mood, color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.25, color=colors[i % len(colors)])

    # Add category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), title='Moods')

    # Pass the figure to st.pyplot
    st.pyplot(fig)