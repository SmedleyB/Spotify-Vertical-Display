from flask import Flask, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# --- CREDENTIALS ---
SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID_FROM_SPOTIFY'
SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET_FROM_SPOTIFY'
SPOTIPY_REDIRECT_URI='http://127.0.0.1:5000/callback'

# --- AUTH SETUP ---
# Added user-modify-playback-state scope for the buttons
scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# Initialize the Authentication Manager (not the client yet)
auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope)

def get_spotify_client():
    """Helper function to retrieve a fresh, authorized Spotify client instance."""
    return spotipy.Spotify(auth_manager=auth_manager)

@app.route('/')
def index():
    # Force an auth check on the main page load
    try:
        get_spotify_client().current_user()
    except Exception:
        pass # Allow the auth flow to start
    return render_template('index.html')

@app.route('/data')
def get_data():
    sp_client = get_spotify_client()
    try:
        playback = sp_client.current_playback()
        
        if not playback or not playback['item']:
            return jsonify({'playing': False})

        item = playback['item']
        
        artist_id = item['artists'][0]['id']
        artist_data = sp_client.artist(artist_id)
        artist_img_url = artist_data['images'][0]['url'] if artist_data['images'] else ""

        current = {
            'playing': True,
            'name': item['name'],
            'artist_name': item['artists'][0]['name'],
            'album_name': item['album']['name'],
            'album_art': item['album']['images'][0]['url'],
            'artist_image': artist_img_url,
            'progress': playback['progress_ms'],
            'duration': item['duration_ms'],
            'is_playing': playback['is_playing'] # Needed for play/pause icon
        }

        queue_data = sp_client.queue()
        next_tracks = []
        for track in queue_data['queue'][:5]:
            art = track['album']['images'][-1]['url'] if track['album']['images'] else ""
            next_tracks.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'art': art
            })

        return jsonify({'current': current, 'queue': next_tracks})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'playing': False, 'error': str(e)})

# --- NEW ROBUST CONTROL ROUTES ---
@app.route('/toggle_playback', methods=['POST'])
def toggle_playback():
    sp_client = get_spotify_client()
    is_playing = sp_client.current_playback().get('is_playing', False)
    sp_client.pause_playback() if is_playing else sp_client.start_playback()
    return jsonify({'status': 'toggled'})

@app.route('/next_track', methods=['POST'])
def next_track():
    get_spotify_client().next_track()
    return jsonify({'status': 'skipped'})

@app.route('/previous_track', methods=['POST'])
def previous_track():
    get_spotify_client().previous_track()
    return jsonify({'status': 'previous'})
# ----------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
