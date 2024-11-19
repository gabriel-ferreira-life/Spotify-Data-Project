import os
from flask import *
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

client_id = "be1b6f758c9d48a7bc17d4542525840e"
client_secret = "b5fee9ec62b84b5bbed44a16310f71c9"
redirect_uri = "http://localhost:5000/callback"
scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))



@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))


@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlits = sp.current_user_playlists()
    playlits_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlits['items']]
    playlits_html = '<br>'.join([f'{name}: {url}' for name, url in playlits_info])
    
    return playlits_html

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
     
if __name__ == "__main__":
    app.run(debug=True)

# # Initialize Spotify client with environment variables
# spotify_client = SpotifyClient(
#     os.getenv("SPOTIFY_AUTHORIZATION_TOKEN"),
#     os.getenv("SPOTIFY_USER_ID")
# )

# @app.route("/create-playlist", methods=["POST"])
# def create_playlist():
#     data = request.get_json()
    
#     # Get playlist name and track IDs from the request JSON
#     playlist_name = data.get("playlist_name", "My Custom Playlist")
#     track_ids = data.get("track_ids", [])
    
#     # Validate input
#     if not track_ids:
#         return jsonify({"error": "Please provide a list of track IDs to populate the playlist."}), 400

#     # Create new playlist
#     playlist = spotify_client.create_playlist(playlist_name)
    
#     # Populate playlist with provided tracks
#     spotify_client.populate_playlist(playlist, track_ids)
    
#     return jsonify({
#         "message": f"Playlist '{playlist_name}' created successfully with provided tracks.",
#         "playlist_id": playlist.id,
#         "track_ids": track_ids
#     })