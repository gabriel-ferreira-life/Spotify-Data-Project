# import os
# from flask import Flask, request, jsonify
# from spotifyclient import

# app = Flask(__name__)

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

# if __name__ == "__main__":
#     app.run(debug=True)