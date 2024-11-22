from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import streamlit as st
import streamlit.components.v1 as components

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = f"{url}?{query}"
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if not json_result:
        st.write("No artist with this name exists...")
        return None
    return json_result[0]

def get_artist_id(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    # Search query for the artist name
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = f"{url}?{query}"
    
    # Send GET request to the Spotify API
    result = get(query_url, headers=headers)
    
    # Parse the JSON response
    json_result = json.loads(result.content)
    
    # Check if any artist is found
    artists = json_result.get("artists", {}).get("items", [])

    # Return the first artist's ID
    artist_id = artists[0]["id"]
    return artist_id

def get_song_id(token,song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={song_name}&type=track&limit=1"
    query_url=f"{url}?{query}"
    result = get(query_url,headers=headers)
    json_result=json.loads(result.content)
    tracks=json_result.get("tracks", {}).get("items", [])

    song_id = tracks[0]["id"]
    print(song_id)
    return song_id

def get_album_id(token,album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query=f"q={album_name}&type=album&limit=1"
    query_url=f"{url}?{query}"
    result=get(query_url, headers=headers)
    json_result=json.loads(result.content)
    albums=json_result.get("albums",{}).get("items",[])

    album_id=albums[0]["id"]
    return album_id

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)['tracks']

def get_genre_songs(token, genres):
    url = "https://api.spotify.com/v1/recommendations"
    genre_seeds = ','.join(genres)

    params = {
        'seed_genres': genre_seeds, 
        'limit': 10 
    }

    headers = get_auth_header(token)
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)
    songs_info = [{'name': track['name'], 
                   'artist': track['artists'][0]['name'], 
                   'album': track['album']['name']} 
                  for track in json_result['tracks']]
    return songs_info

def get_available_genres(token):
    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result['genres']

def make_embed(song):
    url = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{get_song_id(token,song)}?utm_source=generator" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
    return url

def several_browse_categories(token, genres, target_speechiness, target_duration, target_loudness, target_energy, target_valence):
    url = "https://api.spotify.com/v1/recommendations"
    genre_seeds = ','.join(genres)
    params = {
        'seed_genres': genre_seeds,
        'limit': 10,
    }
    if (target_speechiness>0):
        params['target_speechiness']= target_speechiness/100.0
    if(target_duration>0):
        params['target_duration_ms'] = int(target_duration * 60000)
    if(target_loudness>0):
        params['target_loudness'] = -60+target_loudness*(60.0/100)
    if(target_energy>0):
        params['target_energy'] = target_energy/100.0
    if(target_valence>0):
        params['target_valence'] = target_valence/100.0
    headers = get_auth_header(token)
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)
    songs_info = [{'name': track['name'], 
                   'artist': track['artists'][0]['name'], 
                   'album': track['album']['name']} 
                  for track in json_result['tracks']]
    return songs_info

def get_song_data(token, song_id):
    url = f'https://api.spotify.com/v1/audio-features/{song_id}'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    data = {
        'speechiness': json_result['speechiness'],
        'duration_ms': json_result['duration_ms'],
        'loudness': json_result['loudness'],
        'energy': json_result['energy'],
        'valence': json_result['valence']
    }
    return data

def get_genres_based_on_song(token, song_name):
    song_id = get_song_id(token, song_name)

    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    song_data = json.loads(result.content)
    artist_id = song_data['artists'][0]['id']
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_response = get(artist_url, headers=headers)
    artist_info = json.loads(artist_response.content)
    genres = artist_info.get('genres', [])
    return genres[:5]

st.set_page_config(page_title="Spotify Song Recommendations")
token = get_token()
genres = get_available_genres(token)
st.title("Spotify Song Recommender")
st.write("Values left as 0 are ignored in search")

col1, col2 = st.columns(2)

# Column 1: Genres and Speechiness
with col1:
    selected_genres = st.multiselect(
        label="Genres", 
        options=genres,  
        key="genre", 
        max_selections=5
    )
    
    selected_speechiness = st.number_input('How much speech (1-100)?', min_value=0, max_value=100)
    st.write(selected_speechiness)

    selected_duration = st.number_input('How long (minutes)?', min_value=0.0, max_value=10000.0)
    st.write(selected_duration)

# Column 2: Loudness, Energy, and Valence
with col2:
    selected_loudness = st.number_input('How loud (1-100)?', min_value=0, max_value=100)
    st.write(selected_loudness)
    
    selected_energy = st.number_input('How much energy (1-100)?', min_value=0, max_value=100)
    st.write(selected_energy)
    
    selected_valence = st.number_input("How happy (1-100)?", min_value = 0, max_value = 100)
    st.write(selected_valence)


if selected_genres:
    st.write("**Selected Genres:**", ", ".join(selected_genres))
else:
    st.write("No genres selected.")

if st.button("Get Songs", key = 1):
    if selected_genres:
        songs = several_browse_categories(token, selected_genres, selected_speechiness, selected_duration, selected_loudness, selected_energy, selected_valence)
        if songs:
            st.header("**Recommended Songs:**") 
            for i,song in enumerate(songs):
                components.html(make_embed(song['name'])) #Creates an embed for a song(see make_embed function)
        else:
            st.write("No songs found for the selected genres.")
    else:
        st.write("Please select at least one genre")

# selected_song = st.text_input("Or enter a song for recommendations")

# if st.button("Get Songs", key = 2):
#     if selected_song:
#         if get_song_data(token, get_song_id(token, selected_song)):
#             data = get_song_data(token, get_song_id(token, selected_song))
#             print(data)
#             list_genres = get_genres_based_on_song(token, selected_song)
#             songs = several_browse_categories(token, list_genres, int(data['speechiness']*100),data['duration_ms']/60000.0,(data['loudness'] + 60) * (100 / 60),int(data['energy'] * 100),int(data['valence'] * 100))
#             if songs:
#                 if songs:
#                     st.header("**Recommended Songs**")
#                     for i, song in enumerate(songs):
#                         print(song)
#                         components.html(make_embed(song['name']))
#                 else:
#                     st.write("No songs found")
#         else:
#             st.write("No songs found")
#     else:
#         st.write("Please enter a song")