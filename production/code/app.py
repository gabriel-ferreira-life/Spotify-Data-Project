import streamlit as st
from MusicRecommender import MusicRecommender

def main():
    # Instantiate the recommender
    recommender = MusicRecommender()

    # Welcome message
    st.title("Music Recommender")
    st.write("Welcome to the Music Recommender! Please select how you'd like to receive your recommendations.")

    # Recommendation method selection
    method = st.selectbox(
        "How would you like to receive your recommendations?",
        ["Choose an option", "Find similar songs based on a song you like", "Get songs matching your current mood"]
    )

    # Get the number of songs from the user
    top_n = st.slider("How many song recommendations would you like in your playlist?", 1, 20, 1)

    # Option 1: Similar songs based on a specific song
    if method == "Find similar songs based on a song you like":
        song_name = st.text_input("Enter the song you like in the format 'Artist - Track':")

        if song_name:
            similar_songs = recommender.recommend_similar_songs(song_name, top_n)
            if similar_songs is not None and not similar_songs.empty:
                st.write(f"Here are some songs similar to '{song_name}':")
                st.dataframe(similar_songs)
            else:
                st.write(f"No similar songs found for '{song_name}'. Please try another song.")

    # Option 2: Songs based on mood
    elif method == "Get songs matching your current mood":
        # Mood options
        mood_options = ["Happy", "Energetic", "Neutral", "Relaxed", "Melancholic"]
        mood = st.selectbox("Choose a mood that best describes how you're feeling:", mood_options)

        if mood:
            recommendations = recommender.recommend_by_mood(mood, n=top_n)
            if not recommendations.empty:
                st.write(f"Here are some '{mood}' songs to match your mood:")
                st.dataframe(recommendations)
            else:
                st.write(f"Sorry, no songs found for the mood '{mood}'. Please try another mood.")

if __name__ == "__main__":
    main()
