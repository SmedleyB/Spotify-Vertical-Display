# 🎶 Spotify Vertical Now Playing Display

<img width="360" height="640" alt="Untitled" src="https://github.com/user-attachments/assets/396f9078-2b40-407f-bc00-713eb01f376b" />
<img width="360" height="640" alt="Untitled 2png" src="https://github.com/user-attachments/assets/217bd203-107c-46cc-b857-f4b07ae82965" />
<img width="360" height="640" alt="Untitled3" src="https://github.com/user-attachments/assets/6e59265e-2435-4d45-82bf-08cc8391f92b" />

This project is a clean, vertical "Now Playing" display for Spotify, designed specifically for use on portrait-oriented screens, smart displays, or kiosks (I built it to use on a 1080x1920 AIO toucscreen PC). It uses Python (Flask) for backend Spotify authentication and data fetching, combined with HTML/CSS/JavaScript for a dynamic, modern frontend experience.

-----

## ✨ Features

  * **Vertical, Full-Screen Layout:** Optimized for portrait displays (e.g., Raspberry Pi screens, tablets).
  * **Dynamic Color Scheme:** Extracts the dominant color from the album art and uses it to tint the background and UI elements.
  * **Hidden Controls:** Playback controls (Previous, Play/Pause, Next) and the progress bar are hidden by default and appear when the **Artist Image** is clicked or tapped.
  * **Scrolling Queue:** Displays the "Next Up" queue in a clean, horizontally scrolling ticker at the bottom.
  * **Rate Limit Optimized:** Uses a client-side progress bar and a 5-second polling interval to minimize API calls and avoid Spotify rate limiting.


Gestures:
* Tap Album Art: Toggles Play/Pause.
* Tap Artist Photo: Toggles the visibility of the Playback Controls (Next, Previous, Play/Pause).
* Swipe Left/Right (Main Screen): Next/Previous Track.
* Swipe Down (Main Screen): Opens the Artist Photo Gallery.
* Swipe Up (Main Screen): Opens/Closes the Playback Controls.
* Swipe Up (Gallery Open): Closes the Artist Photo Gallery.
* Artist Gallery: Fetches and displays fanart/photos from TheAudioDB using a CORS proxy.
* Minimal Queue: A scrolling ticker showing the next songs in the queue.

-----

## 💻 Setup and Installation

### Prerequisites

Before starting, you need the following installed:

1.  **Python 3.x**
2.  **Spotify Developer Account** (free)
3.  A basic understanding of using the terminal/command line.

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/YourUsername/Spotify-Vertical-Display.git
cd Spotify-Vertical-Display
```

### Step 2: Create a Spotify Developer App

You must register an application with Spotify to get the necessary credentials:

1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2.  Click **"Create App"**.
3.  Fill in the name (e.g., "Vertical Display") and description.
4.  Once the app is created, locate and save your **Client ID** and **Client Secret**.
5.  Click **"Edit Settings"** and add a **Redirect URI**. This must be set to:
    ```
    http://127.0.0.1:5000/callback
    ```
    (Ensure you use HTTP, not HTTPS, for local development.)

### Step 3: Set Up Environment Variables

Edit `app.py` and add your credentials, or don't edit it and create a .env file instead:

```bash
SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID_FROM_SPOTIFY'
SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET_FROM_SPOTIFY'
SPOTIPY_REDIRECT_URI='http://127.0.0.1:5000/callback'
```

### Step 4: Install Dependencies

Install the required Python packages using `pip`. You will need `Flask` for the server and `Spotipy` for the Spotify API interaction.

```bash
pip install flask python-dotenv spotipy
```

*(Note: If you are using a virtual environment, activate it first.)*

-----

## ▶️ Running the Application

### 1\. Start the Flask Server

Run the Python application from your terminal:

```bash
python app.py
```

*(If your file is named differently, use that file name.)*

The server will start, usually running on port 5000. You should see an output similar to:
`* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`

### 2\. Authentication

1.  Open your browser and navigate to: `http://127.0.0.1:5000`
2.  The first time you load the page, you will be redirected to the **Spotify login page**.
3.  Log in and approve the necessary permissions.
4.  You will be redirected back to the display, which should now be active.

***Note:*** *Spotify requires an active playback device. Ensure you have Spotify running on a phone, desktop, or other device to see the "Now Playing" data.*

-----

## 🎨 Design and Usage Notes

### Controls

The playback controls and progress bar are hidden. To reveal them:

1.  **Click/Tap** the **circular Artist Image**.
2.  The controls will fade in.
3.  The progress bar will start updating locally every **0.5 seconds** for smooth animation.
4.  To hide the controls, click the Artist Image again.

### Customization

All styling and frontend logic is contained within the `templates/index.html` file.

  * **Polling Speed:** To adjust the frequency of Spotify API calls, change the `5000` value at the bottom of the `<script>` block in `index.html`:
    ```javascript
    setInterval(updateDisplay, 5000); // Change 5000 to a higher number (e.g., 10000) if you experience rate limiting.
    ```
  * **Aesthetics:** Adjust colors, fonts, and layout using the CSS within the `<style>` tags in `index.html`.
