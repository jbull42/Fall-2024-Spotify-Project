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


@st.cache_data(ttl=timedelta(weeks=1))
def get_all_songs_by_artist(_token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album,single"
    headers = get_auth_header(_token)
    song_result = []
    song_result = get_songs_by_artist(url, headers, artist_id, song_result)
    return song_result


def get_songs_by_artist(url, headers, artist_id, song_result: list): 
    # Get all albums from url
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    album_result = json_result['items']
    for album in album_result:
        # Get ids from all albums
        url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks?limit=50"
        result = get(url, headers=headers)
        song_ids = [song['id'] for song in json.loads(result.content)['items']]
        # Get tracks from song ids
        url = f"https://api.spotify.com/v1/tracks?ids={','.join(song_ids)}"
        result = get(url, headers=headers)
        song_result.extend(json.loads(result.content)['tracks'])

    # Get list of songs with no duplicate song isrc in list
    songs = [song for n, song in enumerate(song_result) if song['external_ids']['isrc'] not in [prev_song['external_ids']['isrc'] for prev_song in song_result[:n]] and song['artists'][0]['id'] == artist_id]

    # Add next page of songs if results are paginated
    if json_result['next'] != None:
        return get_songs_by_artist(json_result['next'], headers, artist_id, songs)
    return songs


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
    # Get ids from all albums
    # url = f"https://api.spotify.com/v1/artists/{artist_id}"
    # headers = get_auth_header(_token)
    # result = get(url, headers=headers)
    # return json.loads(result.content)['popularity']
    popularity = 0
    for song in songs:
        popularity += song['popularity']
    return popularity/len(songs)

def get_average_album_length(songs, artist_id, _token) -> str:
    total_time_ms = 0
    for song in songs:
        total_time_ms += song['duration_ms']
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album"
    headers = get_auth_header(_token)
    result = get(url, headers=headers)
    albums = json.loads(result.content)['items']
    length = timedelta(milliseconds=total_time_ms/len(albums))
    return f"{str(length.seconds//60).zfill(2)}:{str(length.seconds%60).zfill(2)}"

def add_artist(text: str):
    artistName = text
    token = get_token()
    artist = search_for_artist(token, artistName if artistName != "" else 'The Beatles')
    st.write(artist['name'])
    songs = get_all_songs_by_artist(token, artist['id'])
    newData = pd.DataFrame({
        "Name": [artist['name']],
        "Average Length": [get_average_length(songs)],
        "Average Song Popularity": [get_average_popularity(songs)],
        "Average Album Length": [get_average_album_length(songs, artist['id'], token)]
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