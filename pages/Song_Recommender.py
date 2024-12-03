import streamlit as st
import requests
import os

# Spotify API credentials (replace with your actual credentials)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Function to get Spotify API token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    if auth_response.status_code != 200:
        raise Exception(f"Spotify API error: {auth_response.status_code} - {auth_response.text}")

    return auth_response.json()['access_token']

# Function to fetch song recommendations from Spotify API
def fetch_song_recommendations(token, genre, mood, decade, music_type):
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        'seed_genres': genre,
        'limit': 10,
        'market': 'US',
        'min_valence': mood[0],
        'max_valence': mood[1],
        'min_acousticness': music_type.get('min_acousticness', 0),
        'max_acousticness': music_type.get('max_acousticness', 1),
        'min_instrumentalness': music_type.get('min_instrumentalness', 0),
        'max_instrumentalness': music_type.get('max_instrumentalness', 1),
        'min_year': decade[0],
        'max_year': decade[1],
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Spotify API error: {response.status_code} - {response.text}")

    return response.json().get('tracks', [])

# Get Spotify token
token = get_spotify_token(client_id, client_secret)

# User inputs
st.title('Music Preference Survey')

genre = st.selectbox('What genre do you prefer?', ['pop', 'rock', 'hip-hop', 'jazz', 'classical', 'country'])
mood = st.selectbox('What mood of music would you like?', ['happy', 'sad', 'energetic', 'calm'])
decade = st.selectbox('What decade would yo ulike the music from?', ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s'])
music_type = st.selectbox('What type of music do you like?', ['acoustic', 'instrumental', 'vocals', 'electronic', 'live', 'remix', 'covers'])

mood_values = {
    'happy': (0.6, 1.0),
    'sad': (0.0, 0.4),
    'energetic': (0.6, 1.0),
    'calm': (0.0, 0.4),
}

decade_years = {
    '1960s': (1960, 1969),
    '1970s': (1970, 1979),
    '1980s': (1980, 1989),
    '1990s': (1990, 1999),
    '2000s': (2000, 2009),
    '2010s': (2010, 2019),
}

music_type_values = {
    'acoustic': {'min_acousticness': 0.7},
    'instrumental': {'min_instrumentalness': 0.5},
    'vocals': {'max_instrumentalness': 0.5},
    'electronic': {'min_acousticness': 0.0, 'max_acousticness': 0.3},
    'live': {'min_liveness': 0.8},
    'remix': {'min_valence': 0.4},
    'covers': {'max_acousticness': 0.6, 'max_instrumentalness': 0.6},
}


if st.button('Get Recommendations'):
    recommendations = fetch_song_recommendations(
        token, genre, mood_values[mood], decade_years[decade], music_type_values[music_type]
    )

    if recommendations:
        st.subheader('Song Recommendations:')
        for track in recommendations:  # Loop through all recommendations and display them
            st.write(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])} - [Listen on Spotify]({track['external_urls']['spotify']})")

    else:
        st.write("No recommendations found.")

