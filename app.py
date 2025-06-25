
import streamlit as st
import pandas as pd
import requests
from scan_titles_weighted import scan_titles_weighted

st.set_page_config(page_title="YouTube Video Title Scanner", layout="centered")

st.title("YouTube Video Title Scanner")
st.markdown("Scan a YouTube channel for advertiser-unfriendly words and suggest safer alternatives.")

api_key = st.text_input("Enter your YouTube Data API Key", type="password")
channel_id = st.text_input("Enter the YouTube Channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)")

max_results = st.number_input("Maximum number of titles to fetch", min_value=1, max_value=500, value=100)

if st.button("Scan Titles") and api_key and channel_id:
    try:
        st.info("Fetching video titles...")
        url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet&type=video&maxResults={max_results}&order=date"
        response = requests.get(url)
        videos = response.json()

        titles = [item['snippet']['title'] for item in videos.get('items', [])]
        if not titles:
            st.warning("No titles found or API quota exceeded.")
        else:
            df_results = scan_titles_weighted(titles, pd.read_csv('updated_keywords.csv'))
            st.success("Scan complete!")
            st.dataframe(df_results)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
