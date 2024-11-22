from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

import streamlit as st

import spotipy
from spotipy.oauth2 import SpotifyOAuth


import warnings 
warnings.filterwarnings ('ignore')

# st.set_page_config(
#     page_title="Hello"
# )

load_dotenv()
client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")

SPOTIPY_CLIENT_ID = '2fcfc322766641a99d65ece7b0f65e0b'
SPOTIPY_CLIENT_SECRET = '985fb18bdb0047f1ae8b627ca8cd184e'
SPOTIPY_REDIRECT_URI = 'http://localhost:3000'  
scope = 'playlist-modify-public'

def get_token():
    auth_string = client_id+":"+client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization":"Basic "+ auth_base64,
        "Content-Type":"application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token=json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization":"Bearer " + token}

def search_for_artist(token, artist_name):
    url="https://api.spotify.com/v1/search"
    headers=get_auth_header(token)
    query=f"q={artist_name}&type=artist&limit=1"
    query_url=url+"?"+query
    result=get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result)==0:
        print("No artist with this name exists...")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers=get_auth_header(token)
    result=get(url, headers=headers)
    json_result=json.loads(result.content)["tracks"]
    return json_result

token = get_token()
result = search_for_artist(token, "The Beatles")
print(result)
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)
for idx, song in enumerate(songs):            
    print(str(idx+1)+"."+song['name'])


print(client_id)
print(client_secret)

st.set_page_config(
    page_title="Hello"
)

## make sure spotify works and your accound it valid 
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))


## get recommendations based on user
def get_recommendations(sp, genre=None, artist_name=None, popularity=None, limit=100):
    seed_genres = [genre] if genre else []
    seed_artists = []
    ## Get user to put in the preferred genre
    genre = input("Enter preferred genre (e.g., pop, rock, jazz): ").strip().lower()
    ## Get user to put in preferred artist if they want to
    artist_name = input("Enter preferred artist (optional): ").strip()
    ## if do put in preferred artist then find artist ID from artist name
    if artist_name:
        artist_results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        if artist_results['artists']['items']:
            seed_artists = [artist_results['artists']['items'][0]['id']]
    ## Get user to put in preferred popularity percentage if they want to
    popularity = int(input("Enter target track popularity (0-100, optional): ").strip())
     ## Get track recommendations
    recommendations = sp.recommendations(seed_genres=seed_genres, seed_artists=seed_artists, target_popularity=popularity, limit=limit)
     ## Get track details
    recommended_tracks = []
    for track in recommendations['tracks']:
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
        }
        recommended_tracks.append(track_info)
    
    print(recommended_tracks)
    return recommended_tracks

    if recommendations:
        print("\nRecommended Tracks:")
        for i, track in enumerate(recommendations, 1):
            print(f"{i}. {track['name']} by {track['artist']} - Album: {track['album']}")
            print(f"   Spotify Link: {track['spotify_url']}")
            print(f"   Preview URL: {track['preview_url']}\n")
    else:
        print("No recommendations found")

get_recommendations (sp, genre = None, artist_name = None, popularity = None, limit =100)

