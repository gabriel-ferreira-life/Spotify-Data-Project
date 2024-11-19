import os
import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

client_id = "be1b6f758c9d48a7bc17d4542525840e"
client_secret = "b5fee9ec62b84b5bbed44a16310f71c9"
redirect_uri = "http://localhost:8501"
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
    # Check for cached token
    token_info = sp_oauth.get_cached_token()
    
    if not token_info:
        # Display the authorization URL for the user
        auth_url = sp_oauth.get_authorize_url()
        st.write("Please authenticate with Spotify:")
        st.write(f"[Click here to authenticate]({auth_url})")
        
        # Extract the authorization code from the URL
        code = st.query_params().get("code")
        if code:
            token_info = sp_oauth.get_access_token(code[0])
    
    if token_info:
        return Spotify(auth=token_info['access_token'])
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