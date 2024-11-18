import streamlit as st
from MusicRecommender import MusicRecommender
import numpy as np
from helper import standardize_date, search_songs, search_artist

@st.cache_data
def initiate_class():
    return MusicRecommender()

def show_recomendation_page():
    # Instantiate the recommender
    recommender = initiate_class()

    # Welcome message
    st.title("Music Recommender")
    st.write("Welcome to the Music Recommender! Please select how you'd like to receive your recommendations.")

    ## Get User Input ##
    # Recommendation method selection
    method = st.selectbox(
        "How would you like to receive your recommendations?",
        ["Choose an option", "Find similar songs based on a song you like", "Get songs matching your current mood"]
    )

    ## Recommendation Options ##
    #################################################################################
    # Option 1: Similar songs based on a specific song
    if method == "Find similar songs based on a song you like":
        
        # Getting preprocessed data
        data = recommender.preprocessed_songs

        # Initialize session state variables if they don't exist
        if 'song_name_clicked' not in st.session_state:
            st.session_state.song_name_clicked = False
        if 'artist_name_clicked' not in st.session_state:
            st.session_state.artist_name_clicked = False

        # Display two buttons side by side
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Song Name"):
                st.session_state.song_name_clicked = True
                st.session_state.artist_name_clicked = False

        with col2:
            if st.button("Artist Name"):
                st.session_state.artist_name_clicked = True
                st.session_state.song_name_clicked = False

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






        # Get the number of songs from the user
        top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 1)

        # Go button
        get_recommendations = st.button("Get Recommendations")
        if get_recommendations:

            if song_name:
                similar_songs = recommender.recommend_similar_songs(song_name, top_n)
                if similar_songs is not None and not similar_songs.empty:
                    st.write(f"Here are some songs similar to '{song_name}':")
                    st.dataframe(similar_songs)
                else:
                    st.write(f"No similar songs found for '{song_name}'. Please try another song.")




    #################################################################################
    # Option 2: Songs based on mood
    elif method == "Get songs matching your current mood":
        # Mood options
        mood_options = ["Happy", "Energetic", "Neutral", "Relaxed", "Melancholic"]
        mood = st.selectbox("Choose a mood that best describes how you're feeling:", mood_options)

        # Get the number of songs from the user
        top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 1)

        # Go button
        get_recommendations = st.button("Get Recommendations")
        if get_recommendations:

            if mood:
                recommendations = recommender.recommend_by_mood(mood, top_n)
                if not recommendations.empty:
                    st.write(f"Here are some '{mood}' songs to match your mood:")
                    st.dataframe(recommendations)
                else:
                    st.write(f"Sorry, no songs found for the mood '{mood}'. Please try another mood.")