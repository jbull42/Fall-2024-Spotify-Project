import streamlit as st
import os
import base64
import requests
from requests import post, get
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import math
from streamlit_option_menu import option_menu
from Home import get_token, get_auth_header, search_for_artist

st.set_page_config(page_title="Playlist Generator")
st.sidebar.header("Playlist Generator")
st.write("# Playlist Generator")
st.write("#### Answer some questions to get started")
load_dotenv()


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

token = get_token()
st.write("token:", token)

def get_album_tracks(headers, id):
    url = "https://api.spotify.com/v1/albums/" + id + "/tracks"
    result = get(query, headers=headers)
    json_result = json.loads(result.content)
    ids = []
    for idx in json_result['tracks']['items']:
        ids.append(idx['id'])
    return ids

def get_audio_features(headers, id):
    url = "https://api.spotify.com/v1/audio-features/" + id
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    st.write(json_result)
    dance = json_result['danceability']
    energy = json_result['energy']
    loudness = json_result['loudness']
    mode = json_result['mode']
    speech = json_result['speechiness']
    acoustic = json_result['acousticness']
    instrum = json_result['instrumentalness']
    live = json_result['valence']
    valence = json_result['valence']
    tempo = json_result['tempo']
    features = {"dance" : dance, "energy" : energy, "loudness" : loudness, "mode" : mode, "speech" : speech, "acoustic" : acoustic, \
        "instrum" : instrum, "live" : live, "valence" : valence, "tempo" : tempo}
    return features

def average_features(features):
    total = len(features)
    dance = 0
    energy = 0
    loudness = 0
    mode = 0
    speech = 0
    acoustic = 0
    instrum = 0
    live = 0
    valence = 0
    tempo = 0
    for feature in features:
        dance += feature['dance']
        energy += feature['energy']
        loudness += feature['loudness']
        mode += feature['mode']
        speech += feature['speech']
        acoustic += feature['acoustic']
        instrum += feature['instrum']
        live += feature['live']
        valence += feature['valence']
        tempo += feature['tempo']


    avgs = {"dance" : dance/total, "energy" : energy/total, "loudness" : loudness/total, "mode" : mode/total, "speech" : speech/total, \
         "acoustic" : acoustic/total, "instrum" : instrum/total, "live" : live/total, "valence" : valence/total, "tempo" : tempo/total}

    st.write("avgs:", avgs)
    dance = 0
    energy = 0
    loudness = 0
    mode = 0
    speech = 0
    acoustic = 0
    instrum = 0
    live = 0
    valence = 0
    tempo = 0

    for feature in features:
        dance += (feature['dance'] - avgs['dance'])**2
        energy += (feature['energy'] - avgs['energy'])**2
        loudness += (feature['loudness'] - avgs['loudness'])**2
        mode += (feature['mode'] - avgs['mode'])**2
        speech += (feature['speech'] - avgs['speech'])**2
        acoustic += (feature['acoustic'] - avgs['acoustic'])**2
        instrum += (feature['instrum'] - avgs['instrum'])**2
        live += (feature['live'] - avgs['live'])**2
        valence += (feature['valence'] - avgs['valence'])**2
        tempo += (feature['tempo'] - avgs['tempo'])**2

    stds = {"dance" : math.sqrt(dance/total), "energy" : math.sqrt(energy/total), "loudness" : math.sqrt(loudness/total), \
         "mode" : math.sqrt(mode/total), "speech" : math.sqrt(speech/total), "acoustic" : math.sqrt(acoustic/total), \
            "instrum" : math.sqrt(instrum/total), "live" : math.sqrt(live/total), "valence" : math.sqrt(valence/total), \
            "tempo" : math.sqrt(tempo/total)}
    return avgs,stds,total



def get_recommendations(limit, seed_artists, seed_genres, seed_tracks, min_acousticness, max_acousticness, target_acousticness,\
    min_danceability, max_danceability, target_danceability, min_energy, max_energy, target_energy, min_instrumentalness,\
    max_instrumentalness, target_instrumentalness, min_liveness, max_liveness, target_liveness, min_loudness, max_loudness,\
    target_loudness, min_mode, max_mode, target_mode, min_popularity, max_popularity, target_popularity, min_speechiness,\
    max_speechiness, target_speechiness, min_tempo, max_tempo, target_tempo, min_valence, max_valence, target_valence):
    global token
    url = "https://api.spotify.com/v1/recommendations"
    st.write(url)
    headers = {"Authorization" : "Bearer " + token} #, "Content-Type" : "application/json"}
    params = {
        "limit": limit,
        "seed_artists": seed_artists,
        "seed_genres": seed_genres,
        "seed_tracks": seed_tracks,
        "min_acousticness": min_acousticness,
        "max_acousticness": max_acousticness,
        "target_acousticness": target_acousticness,
        "min_danceability": min_danceability,
        "max_danceability": max_danceability,
        "target_danceability": target_danceability,
        "min_energy": min_energy,
        "max_energy": max_energy,
        "target_energy": target_energy,
        "min_instrumentalness": min_instrumentalness,
        "max_instrumentalness": max_instrumentalness,
        "target_instrumentalness": target_instrumentalness,
        "min_liveness": min_liveness,
        "max_liveness": max_liveness,
        "target_liveness": target_liveness,
        "min_loudness": min_loudness,
        "max_loudness": max_loudness,
        "target_loudness": target_loudness,
        "min_mode": min_mode,
        "max_mode": max_mode,
        "target_mode": target_mode,
        "min_popularity": min_popularity,
        "max_popularity": max_popularity,
        "target_popularity": target_popularity,
        "min_speechiness": min_speechiness,
        "max_speechiness": max_speechiness,
        "target_speechiness": target_speechiness,
        "min_tempo": min_tempo,
        "max_tempo": max_tempo,
        "target_tempo": target_tempo,
        "min_valence": min_valence,
        "max_valence": max_valence,
        "target_valence": target_valence
    }
    # params = {key: value for key, value in params.items() if value is not None}
    st.write(params)
    result = requests.get(url, headers=headers, params=params)
    st.write(result)
    print("headers:", headers)
    st.write(headers)
    json_result = result.json()
    st.write(json_result)

def get_seed_track_ids(songs, headers):
    output = []
    st.write(len(songs))
    if len(songs) > 0:
        for song in songs:
            url = "https://api.spotify.com/v1/search"
            query = f"q={song}&type=track&limit=1"
            query_url = url + "?" + query
            result = get(query_url, headers=headers)
            json_result = json.loads(result.content)["tracks"]["items"][0]['id']
            st.write("json result:", json_result)
            if len(json_result) == 0:
                print("No artist with this name exists…")
                return None
            else:
                output.append(json_result)
    return output
    
    
# 136qg5wi07tzddyer6rvb4iti
# with st.form("my_form"):

has_account = st.selectbox(
    "Do you already have a Spotify account?",
    ("Yes", "No"), placeholder="Choose an option",
)
if has_account == "Yes":
   #  headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    account = st.text_input("What is your Spotify username?", placeholder="Enter your Spotify username")
    name = st.text_input("What would you like to name your playlist?", placeholder="Enter the name for your playlist")
    
    '''
    if account and name:  # Ensure both fields are filled

        # Define the URL and headers
        url = f'https://api.spotify.com/v1/users/{name}/playlists'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        st.write(headers)

        # Define the data payload
        data = {
            'name': 'New Playlist',
            'description': 'New playlist description',
            'public': False  # Set public to boolean
        }

        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code != 201:
            json_result = json.loads(response.content)
            st.write("Error creating playlist:", response.status_code, json_result)
        else:
            json_result = json.loads(response.content)
            st.write(json_result)
    else:
        st.write("Please fill in both fields.")
    '''
headers = get_auth_header(token)
st.write(headers)
url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
result = get(url, headers=headers)
json_result = json.loads(result.content)
print("result", str(json_result))
genres = []
for genre in json_result['genres']:
    genres.append(genre)

genres = st.multiselect(
"What genres would you like this playlist to capture? Choose as many as you like",
genres
)

artist_input = st.text_input('Enter your favorite artists whose music you\'d like this playlist to reflect, separated by commas', value="", placeholder = 'Enter artists, separated by commas')
artists = [artist.strip() for artist in artist_input.split(',')]
artist_ids = []
images = []
for idx, artist in enumerate(artists):
    result = search_for_artist(token, artist)
    artists[idx] = result['name']
    artist_ids.append(result['id'])
    for genre in result['genres']:
        genres.append(genre)
    images.append(result['images'][0]['url'])
st.write("Your favorite artists:", ", ".join(artists))
columns = st.columns(len(artists))
for idx, column in enumerate(columns):
    with column:
        st.image(images[idx])


albums = st.text_input('Enter your favorite albums whose music you\'d like this playlist to reflect, separated by commas. \n If you do not have any albums, leave this field blank', value="", placeholder = 'Enter albums, separated by commas')
albums = [album.strip() for album in albums.split(',')]
keys = ['dance', 'energy', 'loudness', 'mode', 'speech', 'acoustic', 'instrum', 'live','valence', 'tempo']
avgs = {key: 0 for key in keys}
stds = {key: 0 for key in keys}
total = 0
if len(albums) > 0:
    for idx, album in enumerate(albums):
        url = "https://api.spotify.com/v1/search"
        query = f"q={album}&type=album&limit=1"
        query_url = url + "?" + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)
        # id stores album id
        id = json_result['albums']['items'][0]['id']
        url = "https://api.spotify.com/v1/albums/"
        query = url + str(id)
        result = get(query, headers=headers)
        json_result = json.loads(result.content)
        tracks = get_album_tracks(headers, id)
        features = []
        for track in tracks:
            features.append(get_audio_features(headers, track))
        album_avgs = average_features(features)[0]
        album_stds = average_features(features)[1]
        total_tracks = average_features(features)[2]
        for avg in album_avgs:
            avgs[avg] += album_avgs[avg]
            value1 = math.sqrt((((total_tracks - 1)*((album_stds[avg])**2)) + (total-1)*((stds[avg])**2)) / (total_tracks + total - 2))
            value2 = math.sqrt((total_tracks * total) / (total_tracks + total))
            stds[avg] = value1 * value2
            total += total_tracks

songs = st.text_input('Enter your favorite songs that you\'d like this playlist to reflect, separated by commas. \n If you do not have any songs, leave this field blank', value="", placeholder = 'Enter songs, separated by commas')

seed_track_names = [song.strip() for song in songs.split(',')]
seed_track_ids = get_seed_track_ids(seed_track_names, headers)
print("seed track names:", seed_track_names)
print("seed track ids:", seed_track_ids)


limit = albums = st.text_input('How many tracks would you like your playlist to contain?', value="", placeholder = 'Enter a number')
min_popularity, max_popularity = st.slider("Choose how popular you would like the songs in your playlist to be (0 for least popular, 100 for most popular", 0, 100, (0, 100))
target_popularity = (min_popularity + max_popularity) / 2
seed_artists = ",".join(artist_ids)
genres = genres[1]
st.write("genre", genres, len(genres))
if not isinstance(genres, str): 
    seed_genres = ",".join(genres)
else:
    seed_genres = genres
    st.write('yes')
st.write(seed_genres)
# seed_genres = seed_genres.replace(" ", "+")
seed_tracks = ""
if len(seed_track_ids) > 1:
    print('yes')
    seed_tracks = str(",".join(seed_track_ids))
else:
    seed_tracks = seed_track_ids[0]
print("seed tracks:", seed_tracks)
if stds['acoustic'] > avgs['acoustic']:
    min_acousticness = 0
else:
    min_acousticness = avgs['acoustic'] - stds['acoustic']
if avgs['acoustic'] + stds['acoustic'] > 1:
    max_acousticness = 1
else:
    max_acousticness = avgs['acoustic'] + stds['acoustic']
target_acousticness = avgs['acoustic']
if stds['dance'] > avgs['dance']:
    min_danceability = 0
else:
    min_danceability = avgs['dance'] - stds['dance']
if avgs['dance'] + stds['dance'] > 1:
    max_danceability = 1
else:
    max_danceability = avgs['dance'] + stds['dance']
target_danceability = avgs['dance']
if stds['energy'] > avgs['energy']:
    min_energy = 0
else:
    min_energy = avgs['energy'] - stds['energy']
if avgs['energy'] + stds['energy'] > 1:
    max_energy = 1
else:
    max_energy = avgs['energy'] + stds['energy']
target_energy = avgs['energy']
if stds['instrum'] > avgs['instrum']:
    min_instrumentalness = 0
else:
    min_instrumentalness = avgs['instrum'] - stds['instrum']
if avgs['instrum'] + stds['instrum'] > 1:
    max_instrumentalness = 1
else:
    max_instrumentalness = avgs['instrum'] + stds['instrum']
target_instrumentalness = avgs['instrum']
if stds['live'] > avgs['live']:
    min_liveness = 0
else:
    min_liveness = avgs['live'] - stds['live']
if avgs['live'] + stds['live'] > 1:
    max_liveness = 1
else:
    max_liveness = avgs['live'] + stds['live']
target_liveness = avgs['live']
min_loudness = avgs['loudness'] - stds['loudness']
max_loudness = avgs['loudness'] + stds['loudness']
target_loudness = avgs['loudness']
if stds['mode'] > avgs['mode']:
    min_mode = 0
else:
    min_mode = avgs['mode'] - stds['mode']
if avgs['mode'] + stds['mode'] > 1:
    max_mode = 1
else:
    max_mode = avgs['mode'] + stds['mode']
target_mode = avgs['mode']
if stds['speech'] > avgs['speech']:
    min_speechiness = 0
else:
    min_speechiness = avgs['speech'] - stds['speech']
if avgs['speech'] + stds['speech'] > 1:
    max_speechiness = 1
else:
    max_speechiness = avgs['speech'] + stds['speech']
target_speechiness = avgs['speech']
min_tempo = avgs['tempo'] - stds['tempo']
max_tempo = avgs['tempo'] + stds['tempo']
target_tempo = avgs['tempo']
if stds['valence'] > avgs['valence']:
    min_valence = 0
else:
    min_valence = avgs['valence'] - stds['valence']
if avgs['valence'] + stds['valence'] > 1:
    max_valence = 1
else:
    max_valence = avgs['valence'] + stds['valence']
target_valence = avgs['valence']

st.write("get recommend", get_recommendations(limit, seed_artists, seed_genres, seed_tracks, min_acousticness, max_acousticness, target_acousticness, min_danceability, max_danceability, target_danceability, min_energy, max_energy, target_energy, min_instrumentalness, max_instrumentalness, target_instrumentalness, min_liveness, max_liveness, target_liveness, min_loudness, max_loudness, target_loudness, min_mode, max_mode, target_mode, min_popularity, max_popularity, target_popularity, min_speechiness, max_speechiness, target_speechiness, min_tempo, max_tempo, target_tempo, min_valence, max_valence, target_valence))
    
# submitted = st.form_submit_button("Submit")

    

    

