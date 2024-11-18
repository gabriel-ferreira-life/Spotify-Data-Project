from MusicRecommender import MusicRecommender

def main():
    # Instantiate the recommender
    recommender = MusicRecommender()

    # Prompt user to select recommendation method
    print("Welcome to the Music Recommender!")
    method = input("\nHow would you like to receive your recommendations?\n"
                   "Enter '1' to find similar songs based on a song you like\n"
                   "Enter '2' to get songs matching your current mood\n"
                   "Your choice (1 or 2): ")

    # Get the number of songs the user wants in their playlist, with error handling
    try:
        top_n = int(input("\nHow many song recommendations would you like in your playlist? "))
        if top_n <= 0:
            raise ValueError
    except ValueError:
        print("\nInvalid input. Please enter a positive integer for the number of songs.")
        return

    # Option 1: Similar songs based on a specific song
    if method == "1":
        song_name = input("\nEnter the song you like in the format 'Artist - Track': ")
        similar_songs = recommender.recommend_similar_songs(song_name, top_n)
        
        if similar_songs is not None and not similar_songs.empty:
            print(f"\nHere are some songs similar to '{song_name}'")
            print(similar_songs.to_string(index=False))
        else:
            print(f"\nNo similar songs found for '{song_name}'. Please try another song.")

    # Option 2: Songs based on mood
    elif method == "2":
        # Mood options mapped to user input
        mood_options = {
            "1": "Happy",
            "2": "Energetic",
            "3": "Neutral",
            "4": "Relaxed",
            "5": "Melancholic"
        }
        
        print("\nWhich mood are you in?")
        for key, value in mood_options.items():
            print(f"  {key} - {value}")
        
        mood_choice = input("Choose a number that best describes your mood: ")

        mood = mood_options.get(mood_choice)
        
        if mood:
            recommendations = recommender.recommend_by_mood(mood, n=top_n)
            if not recommendations.empty:
                print(f"\nHere are some '{mood}' songs to match your mood:")
                print(recommendations.to_string(index=False))
            else:
                print(f"\nSorry, no songs found for the mood '{mood}'. Please try another mood.")
        else:
            print("\nInvalid mood selection. Please restart and choose a valid option.")

    else:
        print("\nInvalid selection. Please restart and choose either '1' or '2'.")

if __name__ == "__main__":
    main()