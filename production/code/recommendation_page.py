import streamlit as st
import numpy as np

def show_recomendation_page():
    st.title("Music Recommendation with Spotify")

    st.write("""### Recommend based on music Similarity""")

    recommendation_methods = (
        "Choose",
        "Song Similarity Based",
        "Mood Based"
    )

    recommendation_method = st.selectbox("Recommendation Methods Available", recommendation_methods)

    if recommendation_method == "Mood Based":

        mood_options = (
            "Choose",
            "Happy",
            "Energetic",
            "Neutral",
            "Relaxed",
            "Melancholic"
        )
        
        mood = st.selectbox("Moods", mood_options)

        # # Display the selected mood
        # st.write(f"You selected: {mood}")