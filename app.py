from flask import Flask, render_template, jsonify, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- CREDENTIALS FROM ENVIRONMENT ---
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:5000/callback')
SPOTIPY_CACHE_PATH = os.getenv('SPOTIPY_CACHE_PATH', '.spotify-token-cache')

# --- AUTH SETUP ---
# Added user-modify-playback-state scope for the buttons
SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

def make_auth_manager():
    """Create a SpotifyOAuth instance with cache support."""
    if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
        raise ValueError("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set in environment variables")
    
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=SPOTIPY_CACHE_PATH
    )

def get_spotify_client():
    """Helper function to retrieve a fresh, authorized Spotify client instance.
    Returns None if not authenticated."""
    try:
        auth_manager = make_auth_manager()
        token_info = auth_manager.get_cached_token()
        
        if not token_info:
            return None
        
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"Error getting Spotify client: {e}")
        return None

def safe_get(dictionary, *keys, default=None):
    """Safely get nested dictionary values."""
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default

def safe_first(lst, default=None):
    """Safely get the first element of a list."""
    return lst[0] if lst and len(lst) > 0 else default

@app.route('/authorize')
def authorize():
    """Redirect to Spotify authorization page."""
    try:
        auth_manager = make_auth_manager()
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)
    except Exception as e:
        return jsonify({'error': f'Authorization failed: {str(e)}'}), 500

@app.route('/callback')
def callback():
    """Handle OAuth callback from Spotify."""
    try:
        auth_manager = make_auth_manager()
        code = request.args.get('code')
        
        if not code:
            return jsonify({'error': 'No authorization code provided'}), 400
        
        # Exchange code for access token
        auth_manager.get_access_token(code, as_dict=False)
        
        # Redirect to home page
        return redirect('/')
    except Exception as e:
        return jsonify({'error': f'Callback failed: {str(e)}'}), 500

@app.route('/')
def index():
    """Main page - check authentication and redirect if needed."""
    sp_client = get_spotify_client()
    
    # If not authenticated, redirect to authorization
    if sp_client is None:
        return redirect('/authorize')
    
    # Try to verify the client works
    try:
        sp_client.current_user()
    except Exception:
        # Token might be expired or invalid
        return redirect('/authorize')
    
    return render_template('index.html')

@app.route('/data')
def get_data():
    """Get current playback data."""
    sp_client = get_spotify_client()
    
    # Check authentication
    if sp_client is None:
        return jsonify({'playing': False, 'error': 'unauthenticated'}), 200
    
    try:
        playback = sp_client.current_playback()
        
        if not playback or not playback.get('item'):
            return jsonify({'playing': False})

        item = playback['item']
        
        # Defensive access for artist data
        artist_id = safe_get(item, 'artists', 0, 'id')
        artist_img_url = ""
        
        if artist_id:
            try:
                artist_data = sp_client.artist(artist_id)
                # Safely get first image or empty string
                artist_images = safe_get(artist_data, 'images', default=[])
                artist_img_url = safe_get(safe_first(artist_images), 'url', default="")
            except Exception as e:
                print(f"Error fetching artist data: {e}")

        # Safely get album art
        album_images = safe_get(item, 'album', 'images', default=[])
        album_art = safe_get(safe_first(album_images), 'url', default="")
        
        # Safely get artist name
        artist_name = safe_get(item, 'artists', 0, 'name', default="Unknown Artist")

        current = {
            'playing': True,
            'name': item.get('name', 'Unknown Track'),
            'artist_name': artist_name,
            'album_name': safe_get(item, 'album', 'name', default="Unknown Album"),
            'album_art': album_art,
            'artist_image': artist_img_url,
            'progress': playback.get('progress_ms', 0),
            'duration': item.get('duration_ms', 0),
            'is_playing': playback.get('is_playing', False)
        }

        # Get queue with defensive checks
        next_tracks = []
        try:
            queue_data = sp_client.queue()
            queue_list = safe_get(queue_data, 'queue', default=[])
            
            for track in queue_list[:5]:
                track_images = safe_get(track, 'album', 'images', default=[])
                # Get last image (smallest size) if available
                art = safe_get(track_images[-1] if track_images else None, 'url', default="")
                track_artists = safe_get(track, 'artists', default=[])
                
                next_tracks.append({
                    'name': track.get('name', 'Unknown'),
                    'artist': safe_get(safe_first(track_artists), 'name', default="Unknown"),
                    'art': art
                })
        except Exception as e:
            print(f"Error fetching queue: {e}")

        return jsonify({'current': current, 'queue': next_tracks})

    except Exception as e:
        print(f"Error in /data: {e}")
        return jsonify({'playing': False, 'error': str(e)})

@app.route('/control', methods=['POST'])
def control():
    """Unified control endpoint for playback actions."""
    sp_client = get_spotify_client()
    
    # Check authentication
    if sp_client is None:
        return jsonify({'ok': False, 'error': 'unauthenticated'}), 401
    
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'ok': False, 'error': 'Missing action parameter'}), 400
        
        action = data['action']
        
        if action == 'next':
            sp_client.next_track()
            return jsonify({'ok': True, 'action': 'next'})
        
        elif action == 'previous':
            sp_client.previous_track()
            return jsonify({'ok': True, 'action': 'previous'})
        
        elif action == 'toggle':
            # Get current playback state
            playback = sp_client.current_playback()
            if not playback:
                return jsonify({'ok': False, 'error': 'No active playback'}), 400
            
            is_playing = playback.get('is_playing', False)
            
            if is_playing:
                sp_client.pause_playback()
                return jsonify({'ok': True, 'action': 'pause'})
            else:
                sp_client.start_playback()
                return jsonify({'ok': True, 'action': 'play'})
        
        else:
            return jsonify({'ok': False, 'error': f'Unknown action: {action}'}), 400
    
    except spotipy.exceptions.SpotifyException as e:
        # Handle Spotify API errors
        status_code = e.http_status if hasattr(e, 'http_status') else 500
        return jsonify({'ok': False, 'error': str(e)}), status_code
    
    except Exception as e:
        print(f"Error in /control: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# --- LEGACY ENDPOINTS (kept for backward compatibility) ---
@app.route('/toggle_playback', methods=['POST'])
def toggle_playback():
    """Legacy endpoint - redirects to /control."""
    sp_client = get_spotify_client()
    if sp_client is None:
        return jsonify({'status': 'error', 'message': 'unauthenticated'}), 401
    
    try:
        playback = sp_client.current_playback()
        is_playing = safe_get(playback, 'is_playing', default=False) if playback else False
        
        if is_playing:
            sp_client.pause_playback()
        else:
            sp_client.start_playback()
        
        return jsonify({'status': 'toggled'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/next_track', methods=['POST'])
def next_track():
    """Legacy endpoint - redirects to /control."""
    sp_client = get_spotify_client()
    if sp_client is None:
        return jsonify({'status': 'error', 'message': 'unauthenticated'}), 401
    
    try:
        sp_client.next_track()
        return jsonify({'status': 'skipped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/previous_track', methods=['POST'])
def previous_track():
    """Legacy endpoint - redirects to /control."""
    sp_client = get_spotify_client()
    if sp_client is None:
        return jsonify({'status': 'error', 'message': 'unauthenticated'}), 401
    
    try:
        sp_client.previous_track()
        return jsonify({'status': 'previous'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
