import os
import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

client_id = "be1b6f758c9d48a7bc17d4542525840e"
client_secret = "b5fee9ec62b84b5bbed44a16310f71c9"
redirect_uri = "https://simplyfy-recommender-system.streamlit.app"
scope = 'playlist-modify-public'

# Set up Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

# Function to get the Spotify access token
def get_spotify_client():
    # Check if the token is already cached in session state
    if 'token_info' not in st.session_state:
        st.session_state.token_info = None

    # Display the authorization URL if there's no token
    if not st.session_state.token_info:
        auth_url = sp_oauth.get_authorize_url()
        st.write("Please authenticate with Spotify:")
        st.write(f"[Click here to authenticate]({auth_url})")

        # Extract the authorization code from the query parameters
        query_params = st.experimental_get_query_params()
        code = query_params.get("code")

        if code:
            # Exchange the authorization code for a token
            st.session_state.token_info = sp_oauth.get_access_token(code[0])

    # If we have a valid token, return the Spotify client
    if st.session_state.token_info and not sp_oauth.is_token_expired(st.session_state.token_info):
        return Spotify(auth=st.session_state.token_info['access_token'])
    else:
        return None

# Function to create a Spotify playlist and add tracks
def create_spotify_playlist(spotify_client, user_id, playlist_name, track_uris):
    # Create a new playlist
    playlist = spotify_client.user_playlist_create(user_id, playlist_name)
    playlist_id = playlist['id']

    # Add tracks to the new playlist
    spotify_client.playlist_add_items(playlist_id, track_uris)
    return playlist['external_urls']['spotify']

# Function to handle playlist creation
def handle_playlist_creation(spotify_client, track_uris):
    # Get the current user's ID
    user_id = spotify_client.current_user()["id"]

    # Prompt the user for the playlist name
    playlist_name = st.text_input("Enter a name for your playlist:")

    if playlist_name and track_uris:
        # Check if a playlist with the same name already exists
        existing_playlists = spotify_client.current_user_playlists()
        playlist_names = [playlist['name'] for playlist in existing_playlists['items']]

        if playlist_name in playlist_names:
            # Ask the user if they want to overwrite or choose a new name
            st.write("A playlist with this name already exists.")
            overwrite = st.radio(
                "Would you like to overwrite the existing playlist or choose a different name?",
                ("Choose an option", "Overwrite", "Choose a different name")
            )

            if overwrite == "Overwrite":
                # Find and overwrite the existing playlist
                existing_playlist = next(
                    (playlist for playlist in existing_playlists['items'] if playlist['name'] == playlist_name),
                    None
                )
                if existing_playlist:
                    playlist_id = existing_playlist['id']
                    spotify_client.playlist_replace_items(playlist_id, track_uris)
                    st.write(f"Playlist '{playlist_name}' has been overwritten! [Open Playlist]({existing_playlist['external_urls']['spotify']})")
            elif overwrite == "Choose a different name":
                st.write("Please choose a different name for your playlist.")
        else:
            # Create a new playlist and add tracks
            playlist_url = create_spotify_playlist(spotify_client, user_id, playlist_name, track_uris)
            st.write(f"Playlist created successfully! [Open Playlist]({playlist_url})")
    else:
        st.write("Please provide a valid playlist name.")

# Streamlit app logic
st.title("Spotify Playlist Creator")

# Get the Spotify client
spotify_client = get_spotify_client()

if spotify_client:
    st.write("Successfully authenticated with Spotify!")
    # Example usage: handling playlist creation
    track_uris = ["spotify:track:TRACK_ID_1", "spotify:track:TRACK_ID_2"]  # Replace with actual track URIs
    handle_playlist_creation(spotify_client, track_uris)
else:
    st.write("Waiting for Spotify authentication...")