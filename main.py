# Author: Graham Sorg 
# Project: Spotify Song Analysis Web App
# Description: This web application allows users to search for an artist by name, 
# fetch their top tracks from Spotify using the Spotify API, and display them 
# as clickable buttons. When a song button is clicked, it shows an audio analysis 
# for that song. The app uses client credentials to authenticate with Spotify and retrieve 
# the required data such as artist ID, top tracks, and song information.

from dotenv import load_dotenv
import os
import base64
import streamlit as st
import json
from requests import post, get

# Load environment variables from .env file
load_dotenv()

# Retrieve Spotify API credentials from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Function to obtain access token for Spotify API using client credentials
def get_token():
	auth_string = client_id + ":" + client_secret
	auth_bytes = auth_string.encode("utf-8")
	auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
	url = "https://accounts.spotify.com/api/token"
	headers = {
		"Authorization" : "Basic " + auth_base64,
		"Content-Type" : "application/x-www-form-urlencoded"
	}
	data = {"grant_type" : "client_credentials"}
	result = post(url, headers=headers, data=data)
	json_result = json.loads(result.content)
	token = json_result["access_token"]
	return token

# Function to generate the Authorization header using the access token
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

# Helper method to get the artist's ID from their name
def get_artist_id(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
   
    # Search query for the artist name
    query = f"q={artist_name}&type=artist&limit=1"  # limit=1 to get only the top result
    query_url = f"{url}?{query}"
   
    # Send GET request to the Spotify API
    result = get(query_url, headers=headers)
   
    # Parse the JSON response
    json_result = json.loads(result.content)
   
    # Check if any artist is found
    artists = json_result.get("artists", {}).get("items", [])
    if not artists:
        print("No artist with this name found.")
        return None  
    # Return the first artist's ID
    artist_id = artists[0]["id"]
    return artist_id

# Function to retrieve the top tracks of the artist
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result= json.loads(result.content)["tracks"]
    song_names = [{track['name']} for track in json_result]
    return song_names

# Function to display the formatted song list
def get_song_list(song_names):
    """
    Returns a formatted string of the song list for the given artist.
    """
    song_list = ""
    for index, song in song_names.items():
        song_list += f"{index + 1}. {song[0]}\n"
    return song_list.strip()

# Function to retrieve the audio analysis of a specific song
def get_audio_analysis(token, song_id):
    url = f"https://api.spotify.com/v1/audio-analysis/{song_id}"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        json_result = json.loads(result.content)["track"]["num_samples"]
        return json_result
    else:
        return {"error": "Failed to fetch audio analysis"}

# Main application
if __name__ == "__main__":
    token = get_token()
    st.title("Song Analysis")
    artist_name = st.text_input("", value=None, max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Search artist", disabled=False, label_visibility="visible")
    artist_id = get_artist_id(token, artist_name)
    song_names = get_songs_by_artist(token, artist_id)
    #st.write(song_names)
    # Iterate through the song list and create buttons
    for i, song_list in enumerate(song_names):
        if isinstance(song_list, set):
            song_list = list(song_list)  # Convert set to list
    
        song_name = song_list[0]  # Now it's a list, indexing works
    
        # Display song as a button
        if st.button(f"{i + 1}. {song_name}"):
            # When a button is clicked, show the "test successful" message
            st.text(f"Test successful: {song_name}")