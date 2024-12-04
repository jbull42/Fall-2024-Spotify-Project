from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import streamlit as st
from datetime import timedelta
import pandas as pd

st.set_page_config(
    page_title='Artist Stats'
)

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {"grant_type" : "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    return json_result[0]

# Will return duplicate songs
@st.cache_data(ttl=timedelta(weeks=1))
def get_all_songs_by_artist(_token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album,single"
    headers = get_auth_header(_token)
    song_result = get_songs_by_artist(url, headers, artist_id)
    return song_result


def get_songs_by_artist(url, headers, artist_id) -> list: 
    song_result = list()
    # Get all albums from url
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    album_result = json_result['items']

    for i in range(0, len(album_result), 20):
        url = f"https://api.spotify.com/v1/albums?ids={','.join([album['id'] for album in album_result[i:i+20]])}&limit=50"
        result = get(url, headers=headers)
        albums = json.loads(result.content)['albums']

        for album in albums:
            # Get ids from all albums
            song_ids = [song['id'] for song in album['tracks']['items']]
            # Get tracks from song ids
            url = f"https://api.spotify.com/v1/tracks?ids={','.join(song_ids)}"
            result = get(url, headers=headers)
            tracks = json.loads(result.content)['tracks']
            song_result.extend(tracks)
            if album['tracks']['next'] != None:
                song_result.extend(get_album_tracks(album['tracks']['next'], headers))

    # Add next page of songs if results are paginated
    if json_result['next'] != None:
        song_result.extend(get_songs_by_artist(json_result['next'], headers, artist_id))
        return song_result
    return song_result

def get_album_tracks(url, headers):
    result = get(url, headers=headers)
    album = json.loads(result.content)
    song_ids = [song['id'] for song in album['items']]
    # Get tracks from song ids
    url = f"https://api.spotify.com/v1/tracks?ids={','.join(song_ids)}"
    result = get(url, headers=headers)
    tracks = json.loads(result.content)['tracks']
    if album['next'] != None:
        tracks.extend(get_album_tracks(album['next'], headers))
    return tracks
    

def print_songs_by_artist(songs):
    for i, song in enumerate(songs):
        st.write(str(i+1) + ". " + song['name'])


def get_average_length(songs) -> str:
    total_time_ms = 0
    for song in songs:
        total_time_ms += song['duration_ms']
    length = timedelta(milliseconds=total_time_ms/len(songs))
    return f"{str(length.seconds//60).zfill(2)}:{str(length.seconds%60).zfill(2)}"


def get_average_popularity(songs) -> float:
    popularity = 0
    for song in songs:
        popularity += song['popularity']
    return popularity/len(songs)

def get_average_album_length(all_songs) -> str:
    total_length_ms = 0
    album_list = set()
    for song in all_songs:
        if song['album']['album_type'] == 'album':
            total_length_ms += song['duration_ms']
            album_list.add(song['album']['id'])

    if len(album_list) != 0:
        length = timedelta(milliseconds=total_length_ms/len(album_list))
        return f"{str(length.seconds//60).zfill(2)}:{str(length.seconds%60).zfill(2)}"
    return None

def add_artist(text: str): 
    artistName = text
    token = get_token()
    artist = search_for_artist(token, artistName if artistName != "" else 'The Beatles')
    st.write(artist['name'])
    all_songs = get_all_songs_by_artist(token, artist['id'])

    # Remove all duplicate song isrc and song's main artist not being the searched for artist in list
    songs = [song for n, song in enumerate(all_songs) if song['external_ids']['isrc'] not in [prev_song['external_ids']['isrc'] for prev_song in all_songs[:n]] and song['artists'][0]['id'] == artist['id']]

    newData = pd.DataFrame({
        "Name": [artist['name']],
        "Average Length": [get_average_length(songs)],
        "Average Song Popularity": [get_average_popularity(songs)],
        "Average Album Length": [get_average_album_length(all_songs)]
    })
    df: pd.DataFrame = st.session_state['df']
    if df.empty or newData['Name'].to_dict()[0] not in df.to_dict()['Name'].values():
        df = pd.concat([df, newData], ignore_index=True)
        st.session_state['df'] = df
    st.write(df)

with st.form("my_form"):
    text = st.text_input("Add Artist: ")
    st.form_submit_button()

add_artist(text)