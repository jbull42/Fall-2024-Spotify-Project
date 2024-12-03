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

st.set_page_config(page_title="Home")
st.sidebar.header("Home")
st.logo("/Users/jeremybullis/Desktop/Spotify_test_app/Media/New_Logo_Whitespace.png")
st.write("# Fall 2024 Spotify API Project")
col1, col2 = st.columns([1,1])
with col1:
    st.image("/Users/jeremybullis/Desktop/Spotify_test_app/Media/New_Logo_Whitespace.png", width=250)
with col2:
    st.text('')
    st.text('')
    st.image("/Users/jeremybullis/Desktop/Spotify_test_app/Media/spotify_logo.webp", width=400)

st.header("Project Goal", divider='blue')
st.write("The goal of our project is to provide users with the ability to obtain statistics, query the Spotify API, \
    and obtain song and playlist recommendations based on their preferences.")
st.write("")
st.divider()
st.write("")

st.header("Functionalities", divider='blue')
st.subheader("Playlist Recommendation", divider='green')
st.write("Enter your preferences and receive a custom-made playlist as well as an embedded player to listen to your new playlist")
st.subheader("Movie Soundtracks", divider='green')
st.write("Enter your favorite movie and receive a list of all the songs that were included in its soundtrack")
st.subheader("Automatic Playlist Generation", divider='green')
st.write("Receive a custom playlist generated based on the songs in your Spotify library")
st.subheader("Top Song Generator", divider='green')
st.write("Enter any of your favorite artists and receive a list of their ten most popular songs on Spotify")
st.write("")
st.divider()
st.write("")

st.header("Our Team", divider='blue')
col1, col2, col3 = st.columns([1,1,1])
names = ['/Users/jeremybullis/Desktop/Spotify_test_app/Media/Graham_Sorg.png', \
    '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Edrik_Velasquez.jpg',\
         '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Dilan_Fajardo.jpg', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Laura_Chen.jpg', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Cole_Kerkemeyer.jpeg', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Karthik_Valluri.jpg', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Mitchell_Fein.jpg', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Bren_Nakata.png', \
        '/Users/jeremybullis/Desktop/Spotify_test_app/Media/Jeremy_Bullis.jpg']
with col1:
    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Graham_Sorg.png')
    st.subheader("Graham Sorg", divider='green')
    st.write("##### Major: Computer Science")
    st.write("##### Year: Sophomore")
    st.write("##### Favorite Music Genre: Rap/Hip-Hop")

    st.divider()

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Edrik_Velasquez.jpg')
    st.subheader("Edrik Velasquez", divider='green')
    st.write("##### Major: Computer Engineering")
    st.write("##### Year: Junior")
    st.write("##### Favorite Music Genre: Synth-pop")

    st.divider()

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Jeremy_Bullis.jpg')
    st.subheader("Jeremy Bullis", divider='green')
    st.write("##### Major: Data Science and Analytics")
    st.write("##### Year: Junior")
    st.write("##### Favorite Music Genre: Classic Rock")


with col2:
    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Dilan_Fajardo.jpg')
    st.subheader("Dilan Fajardo", divider='green')
    st.write("##### Major: Data Science and Analytics")
    st.write("##### Year: Sophomore")
    st.write("##### Favorite Music Genre: Hip-hop")

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Cole_Kerkemeyer.jpeg')
    st.subheader("Cole Kerkemeyer", divider='green')
    st.write("##### Major: Computer Science and Data Science")
    st.write("##### Year: Freshman")
    st.write("##### Favorite Music Genre: Classical")

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Laura_Chen.jpg')
    st.subheader("Laura Chen", divider='green')
    st.write("##### Major: Data Science and Analytics")
    st.write("##### Year: Freshman")
    st.write("##### Favorite Music Genre: Pop")
with col3:
    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Karthik_Valluri.jpg')
    st.subheader("Karthik Valluri", divider='green')
    st.write("##### Major: Systems Biology")
    st.write("##### Year: Freshman")
    st.write("##### Favorite Music Genre: Blues")

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Bren_Nakata.png')
    st.subheader("Bren Nakata", divider='green')
    st.write("##### Major: Computer Science")
    st.write("##### Year: Freshman")
    st.write("##### Favorite Music Genre: Pop rock")

    st.image('/Users/jeremybullis/Desktop/Spotify_test_app/Media/Mitchell_Fein.jpg')
    st.subheader("Mitchell Fein", divider='green')
    st.write("##### Major: Computer Science")
    st.write("##### Year: Freshman")
    st.write("##### Favorite Music Genre: Alternative")

st.divider()
st.header("Github Access", divider='blue')
st.write("All files and libraries used in this project are available in our Github repository found below")
st.link_button("Our Github", "https://github.com/jbull42/Fall-2024-Spotify-Project")



load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print("CLIENT ID:", client_id, "\nCLIENT SECRET:", client_secret)


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



