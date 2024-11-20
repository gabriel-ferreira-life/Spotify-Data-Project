import streamlit as st
from MusicRecommender import MusicRecommender
import numpy as np
from helper import standardize_date, search_songs, search_artist
from create_playlist import get_spotify_client, create_spotify_playlist, handle_playlist_creation


@st.cache_data
def initiate_class():
    return MusicRecommender()

def show_recommendation_page():
    # Instantiate the recommender
    recommender = initiate_class()

    # Welcome message
    st.title("Music Recommender")
    st.write("Welcome to the Music Recommender! Please select how you'd like to receive your recommendations.")

    # Initialize session state for recommendations
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'create_playlist_clicked' not in st.session_state:
        st.session_state.create_playlist_clicked = False
    if 'last_method' not in st.session_state:
        st.session_state.last_method = None
    if 'last_mood' not in st.session_state:
        st.session_state.last_mood = None

    # Recommendation method selection
    method = st.selectbox(
        "How would you like to receive your recommendations?",
        ["Choose an option", "Find similar songs based on a song you like", "Get songs matching your current mood"]
    )

    # Reset recommendations if the method has changed
    if method != st.session_state.last_method:
        st.session_state.recommendations = None
        st.session_state.create_playlist_clicked = False
        st.session_state.last_method = method

        

    ############################ Song Similarity Method ############################
    elif method == "Get songs matching your current mood":
        mood_options = ["Happy", "Energetic", "Neutral", "Relaxed", "Melancholic"]
        mood = st.selectbox("Choose a mood that best describes how you're feeling:", mood_options)

        if mood != st.session_state.get("last_mood", None):
            st.session_state.recommendations = None
            st.session_state.create_playlist_clicked = False
            st.session_state.last_mood = mood

        top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 10)

        # Get recommendations based on the selected mood
        if st.button("Get Recommendations"):
            st.session_state.create_playlist_clicked = False
            if mood:
                recommendations = recommender.recommend_by_mood(mood, top_n)
                if not recommendations.empty:
                    st.session_state.recommendations = recommendations
                else:
                    st.write(f"Sorry, no songs found for the mood '{mood}'. Please try another mood.")

        # Display recommendations if they exist
        if st.session_state.get("recommendations") is not None:
            st.write(f"Here are some '{mood}' songs to match your mood:")
            st.dataframe(st.session_state.recommendations)

            # Button to create a Spotify playlist
            if st.button("Create Spotify Playlist"):
                st.session_state.create_playlist_clicked = True

        # Handle playlist creation
        if st.session_state.get("create_playlist_clicked", False):
            # Authenticate the user and get the Spotify client
            spotify_client = get_spotify_client()

            if spotify_client:
                # Create a list of track URIs from the recommendations
                track_uris = st.session_state.recommendations['Song ID'].tolist()

                # Call the playlist creation function
                handle_playlist_creation(spotify_client, track_uris)
            else:
                st.write("Failed to authenticate with Spotify. Please try again.")

