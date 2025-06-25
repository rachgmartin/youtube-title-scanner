import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
DEFAULT_API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- CONFIG ---
API_URL = "https://www.googleapis.com/youtube/v3"

# --- FUNCTIONS ---
def get_channel_id(api_key, channel_input):
    if "@" in channel_input:
        response = requests.get(f"{API_URL}/search?part=snippet&type=channel&q={channel_input}&key={api_key}")
    else:
        channel_id = channel_input.split("/")[-1]
        response = requests.get(f"{API_URL}/channels?part=snippet&id={channel_id}&key={api_key}")
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        return data["items"][0]["id"]
    return None

def get_video_titles(api_key, channel_id, max_results=50):
    titles = []
    url = f"{API_URL}/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults={max_results}"
    response = requests.get(url)
    data = response.json()
    for item in data.get("items", []):
        if item["id"].get("videoId"):
            title = item["snippet"]["title"]
            titles.append(title)
    return titles

def scan_titles(titles, flagged_words):
    results = []
    for title in titles:
        matches = [word for word in flagged_words if word.lower() in title.lower()]
        results.append({"Title": title, "Flagged Words": ", ".join(matches) if matches else "None"})
    return pd.DataFrame(results)

# --- WORD MAPPING ---
FLAGGED_WORDS = [
    "bullied", "shamed", "abuses", "scammed", "addicted", "dumped", "hates", "harassed",
    "revenge", "regret", "toxic", "worst", "evil", "cheating"
]

# --- STREAMLIT UI ---
st.title("YouTube Video Title Scanner")
st.write("Scan a YouTube channel for flagged keywords based on brand safety concerns.")

api_key_input = st.text_input("Enter your YouTube Data API Key", type="password")
channel_input = st.text_input("Enter the YouTube Channel URL or Handle (e.g., @DharMann)")

api_key = api_key_input if api_key_input else DEFAULT_API_KEY

if api_key and channel_input:
    channel_id = get_channel_id(api_key, channel_input)
    if channel_id:
        titles = get_video_titles(api_key, channel_id)
        df_results = scan_titles(titles, FLAGGED_WORDS)
        st.dataframe(df_results)

        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results as CSV", csv, "flagged_titles.csv", "text/csv")
    else:
        st.error("Could not find a valid channel ID. Check the URL or handle and try again.")
