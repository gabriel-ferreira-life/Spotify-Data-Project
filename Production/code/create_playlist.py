import os
import streamlit as st
import uuid
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

client_id = "be1b6f758c9d48a7bc17d4542525840e"
client_secret = "b5fee9ec62b84b5bbed44a16310f71c9"
redirect_uri = "https://simplyfy-recommender-system.streamlit.app"
# redirect_uri = "http://localhost:8501"
scope = 'playlist-modify-public, playlist-modify-private, user-read-private'
# scope = 'playlist-modify-public'

# Set up Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=None,
    show_dialog=True
)


def get_spotify_client():
    # Clear session states for fresh authentication
    if "spotify_client" in st.session_state:
        del st.session_state["spotify_client"]
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user_id" in st.session_state:
        del st.session_state["user_id"]

    # Display the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    st.write("Please authenticate with Spotify:")
    st.markdown(f"[Click here to authenticate]({auth_url})", unsafe_allow_html=True)

    # Extract 'code' from query parameters
    code = st.query_params.get("code")

    try:
        # Exchange the authorization code for an access token
        # st.write("code: ", code)
        # st.write("code 0: ", code[0])
        token_info = sp_oauth.get_access_token(code)
        spotify_client = Spotify(auth=token_info['access_token'])
        current_user = spotify_client.current_user()  # Fetch user info
        st.session_state.spotify_client = spotify_client
        st.session_state.authenticated = True
        st.session_state.user_id = current_user["id"]
        st.write("User ID: ", st.session_state.user_id)

        # Debug user info
        # st.write("Authenticated User Info:", current_user)
        st.success("Authenticated successfully!")
        return spotify_client

    except Exception as e:
        st.error(f"Error during authentication: {e}")


        


# Function to create a playlist and add tracks
def create_spotify_playlist(spotify_client, user_id, playlist_name, track_uris):
    # Create a new playlist
    playlist = spotify_client.user_playlist_create(user_id, playlist_name)
    playlist_id = playlist['id']

    # Add tracks to the playlist
    spotify_client.playlist_add_items(playlist_id, track_uris)
    return playlist['external_urls']['spotify']


def handle_playlist_creation(spotify_client, track_uris):
    """
    Handles the creation or overwriting of a Spotify playlist.

    Parameters:
        spotify_client: The Spotify client object for API requests.
        track_uris (list): A list of track URIs to be added to the playlist.
    """
    # Get the current user's ID 
    
    current_user = spotify_client.current_user()
    # st.write("Authenticated user info:", current_user) ## Debug

    user_id = st.session_state.user_id
    # user_id = current_user["id"]

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