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
    if method == "Find similar songs based on a song you like":
        # Getting preprocessed data
        data = recommender.preprocessed_songs

        # Initialize session state for song and artist clicks
        if 'song_name_clicked' not in st.session_state:
            st.session_state.song_name_clicked = False
        if 'artist_name_clicked' not in st.session_state:
            st.session_state.artist_name_clicked = False

        # Initialize song_name
        song_name = None

        # Display two buttons side by side
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Song Name"):
                st.session_state.song_name_clicked = True
                st.session_state.artist_name_clicked = False
                st.session_state.recommendations = None
                st.session_state.create_playlist_clicked = False

        with col2:
            if st.button("Artist Name"):
                st.session_state.artist_name_clicked = True
                st.session_state.song_name_clicked = False
                st.session_state.recommendations = None
                st.session_state.create_playlist_clicked = False

        # Handle "Song Name" search
        if st.session_state.song_name_clicked:
            partial_song_name = st.text_input("Search for song name:")
            if partial_song_name:
                suggestions = search_songs(data, partial_song_name)
                if not suggestions.empty:
                    selected_song = st.selectbox("Select a song:", suggestions['track_name'] + " - " + suggestions['track_artist'])
                    st.write(f"You selected: {selected_song}")
                    song_name = selected_song.split(" - ")[0]
                else:
                    st.write("No matching songs found.")
            else:
                st.session_state.recommendations = None  # Reset if the text input is cleared

        # Handle "Artist Name" search
        if st.session_state.artist_name_clicked:
            partial_artist_name = st.text_input("Search for artist name:")
            if partial_artist_name:
                artist_suggestions = search_artist(data, partial_artist_name)
                if not artist_suggestions.empty:
                    selected_artist = st.selectbox("Select an artist:", artist_suggestions['track_artist'])
                    song_list = data[data['track_artist'] == selected_artist]["track_name"]
                    song_name = st.selectbox("Select Song: ", song_list)
                    st.write(song_name)
                else:
                    st.write("No matching artists found.")
            else:
                st.session_state.recommendations = None  # Reset if the text input is cleared

        # Get the number of songs from the user
        top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 10)

        # Go button
        if st.button("Get Recommendations"):
            st.session_state.create_playlist_clicked = False
            if song_name:
                recommendations = recommender.recommend_similar_songs(song_name, top_n)
                if not recommendations.empty:
                    st.session_state.recommendations = recommendations
                else:
                    st.write(f"No similar songs found for '{song_name}'. Please try another song.")

        # Display recommendations if they exist
        if st.session_state.recommendations is not None:
            st.write(f"Here are some songs similar to '{song_name}':")
            st.dataframe(st.session_state.recommendations)
            if st.button("Create Spotify Playlist"):
                st.session_state.create_playlist_clicked = True

        # Handle playlist creation
        if st.session_state.create_playlist_clicked:
            spotify_client = get_spotify_client()
            if spotify_client:
                track_uris = st.session_state.recommendations['Song ID'].to_list()
                handle_playlist_creation(spotify_client, track_uris)
            else:
                st.write("Failed to authenticate with Spotify. Please try again.")


    
    ############################ Mood Method ############################
    elif method == "Get songs matching your current mood":
        mood_options = ["Happy", "Energetic", "Neutral", "Relaxed", "Melancholic"]
        mood = st.selectbox("Choose a mood that best describes how you're feeling:", mood_options)

        if mood != st.session_state.last_mood:
            st.session_state.recommendations = None
            st.session_state.create_playlist_clicked = False
            st.session_state.last_mood = mood

        top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 10)

        if st.button("Get Recommendations"):
            st.session_state.create_playlist_clicked = False
            if mood:
                recommendations = recommender.recommend_by_mood(mood, top_n)
                if not recommendations.empty:
                    st.session_state.recommendations = recommendations
                else:
                    st.write(f"Sorry, no songs found for the mood '{mood}'. Please try another mood.")

        if st.session_state.recommendations is not None:
            st.write(f"Here are some '{mood}' songs to match your mood:")
            st.dataframe(st.session_state.recommendations)
            if st.button("Create Spotify Playlist"):
                st.session_state.create_playlist_clicked = True

        if st.session_state.create_playlist_clicked:
            spotify_client = get_spotify_client()
            if spotify_client:
                track_uris = st.session_state.recommendations['Song ID'].tolist()
                handle_playlist_creation(spotify_client, track_uris)
            else:
                st.write("Failed to authenticate with Spotify. Please try again.")
