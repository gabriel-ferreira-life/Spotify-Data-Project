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
    # Check if the token info is in session state
    if 'token_info' not in st.session_state or not st.session_state.token_info:
        st.session_state.token_info = sp_oauth.get_cached_token()

    # If there's no cached token or if the token has expired, prompt for authentication
    if not st.session_state.token_info or sp_oauth.is_token_expired(st.session_state.token_info):
        if st.session_state.token_info and sp_oauth.is_token_expired(st.session_state.token_info):
            # Refresh the token if it has expired
            st.session_state.token_info = sp_oauth.refresh_access_token(st.session_state.token_info['refresh_token'])
        else:
            # Display the authorization URL for the user to authenticate
            auth_url = sp_oauth.get_authorize_url()
            st.write("Please authenticate with Spotify:")
            st.write(f"[Click here to authenticate]({auth_url})")

            # Extract the authorization code from the URL
            query_params = st.experimental_get_query_params()
            code = query_params.get("code")

            if code:
                # Exchange the authorization code for a token
                st.session_state.token_info = sp_oauth.get_access_token(code[0])

    # If we have a valid token, return the Spotify client
    if st.session_state.token_info:
        return Spotify(auth=st.session_state.token_info['access_token'])
    else:
        return None

# Function to create a playlist and add tracks
def create_spotify_playlist(spotify_client, user_id, playlist_name, track_uris):
    # Create a new playlist
    playlist = spotify_client.user_playlist_create(user_id, playlist_name)
    playlist_id = playlist['id']

    # Add tracks to the playlist
    spotify_client.playlist_add_items(playlist_id, track_uris)
    return playlist['external_urls']['spotify']

# Function to handle playlist creation
def handle_playlist_creation(spotify_client, track_uris):
    if not spotify_client:
        st.write("Please authenticate with Spotify before creating a playlist.")
        return

    # Get the current user's ID
    user_id = spotify_client.current_user()["id"]

    # User input for the playlist name
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
                # Find the existing playlist ID
                existing_playlist = next(
                    (playlist for playlist in existing_playlists['items'] if playlist['name'] == playlist_name),
                    None
                )
                if existing_playlist:
                    playlist_id = existing_playlist['id']
                    # Clear the existing playlist and add new tracks
                    spotify_client.playlist_replace_items(playlist_id, track_uris)
                    st.write(f"Playlist '{playlist_name}' has been overwritten! [Open Playlist]({existing_playlist['external_urls']['spotify']})")
            elif overwrite == "Choose a different name":
                st.write("Please choose a different name for your playlist.")
        else:
            # Create the playlist and add tracks
            playlist_url = create_spotify_playlist(spotify_client, user_id, playlist_name, track_uris)
            st.write(f"Playlist created successfully! [Open Playlist]({playlist_url})")
    else:
        st.write("Please provide a valid playlist name.")