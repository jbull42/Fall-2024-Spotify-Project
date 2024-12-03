import os
import base64
import streamlit as st
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from requests import post,get
from requests import post, get

#os.system("python3 -m pip3 install python-dotenv")
#os.system("python3 -m pip3 install requests")
from dotenv import load_dotenv 


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data ={"grant_type" : "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = url + "?" + query 
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No aritsts with this name exists...")
        return None
    return json_result[0]

def get_songs_by_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={album_name}&type=album&limit=1"
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["albums"]["items"]
    if len(json_result) == 0:
        print("No album with this name exists...")
        return None
    return json_result[0]


token = get_token()
result = search_for_artist(token, "The Beatles")
print(result)
artist_id = result["id"]
songs = get_songs_by_artists(token, artist_id)
for idx, song in enumerate(songs):
    print(str(idx + 1) + "." + song['name'])

st.set_page_config(
    page_title="Hello"
)

st.title("Movie Soundtrack Search")
movie_name = st.text_input("Enter the movie name")

def get_wikipedia_tracklist():
    new_movie_name = movie_name.replace("'", "%27")
    movie_name_formatted = new_movie_name.replace(" ", "_")
    wiki_url = f"https://en.wikipedia.org/wiki/{movie_name_formatted}_(soundtrack)"
    
    # Fetch the Wikipedia page
    page = requests.get(wiki_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all tracklist tables
    tracklist_divs = soup.find_all("div", class_="track-listing")
    
    # Extract track titles
    track_titles = []
    for div in tracklist_divs:
        tracklist_table = div.find("table")
        if tracklist_table:
            for row in tracklist_table.find_all("tr")[1:]:  # Skip the header row
                columns = row.find_all("td")
                if len(columns) >= 2:  # Ensure there are columns to process
                    track_title = columns[0].get_text(strip=True)
                    track_titles.append(track_title)

    # Return the extracted track titles
    return track_titles


    
# Button to fetch the soundtrack tracklist
if st.button("Search for Soundtrack"):
    if movie_name:
        # Fetch tracklist from Wikipedia
        track = get_wikipedia_tracklist()
        
        # Display tracklist
        if track:
            st.write(f"Tracklist for {movie_name}")
            for idx, track in enumerate(track, start=1):
                st.write(f"{idx}. {track}")
    else:
        st.write("Please enter a movie name.")