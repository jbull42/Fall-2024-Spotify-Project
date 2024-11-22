import streamlit as st
import os
import base64
from requests import post, get
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from streamlit_option_menu import option_menu



st.set_page_config(
    page_title="Top 10"
)


st.sidebar.header("Popular Songs by Artist")

st.write("# Top Song Generator")

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    print("result:", result)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists…")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

artist_name = ""
artist_name = st.text_input(label="Enter an artist")
token = get_token()
if artist_name != "":
    result = search_for_artist(token, artist_name)
    artist_id = result["id"]
    image = result.get('images', {})[0]
    left, middle, right = st.columns([0.7, 1, 1])
    with middle:
        st.image(image['url'], width=300)
    songs = get_songs_by_artist(token, artist_id)

    st.write("## The top 10 most popular songs by " + str(result["name"]) + " are:")

    left, middle, right = st.columns([2, 1.5, 2])
    with left:
        st.subheader('Song')
        for idx,song in enumerate(songs):
            if idx == 0:
                print(song)
            container = st.container(height=50, border=False)
            container.write(str(idx+1) + ". " + song['name'])
    with right:
        st.subheader('Popularity')
        for idx,song in enumerate(songs):
            container = st.container(height=50, border=False)
            container.write(str(song['popularity']))
    with middle:
        st.subheader("Album")
        for item in songs:
            item = item['album']
            # We assume the "images" field is a dictionary with multiple image sizes
            image = item.get('images', {})[0]
            print("image:", image['url'])
            st.image(image['url'], width=50)


