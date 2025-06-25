
import streamlit as st
import pandas as pd
import requests
import os
import re
from dotenv import load_dotenv

# Load API key
load_dotenv()
DEFAULT_API_KEY = os.getenv("YOUTUBE_API_KEY")

API_URL = "https://www.googleapis.com/youtube/v3"

WORD_MAP = {
    "bullied": "teased", "shamed": "judged", "abuses": "mistreats", "scammed": "misled",
    "addicted": "struggling", "dumped": "left", "hates": "dislikes", "harassed": "bothered",
    "revenge": "gets even", "regret": "rethink", "toxic": "controlling", "worst": "challenging",
    "evil": "unfair", "cheating": "dishonest", "racist": "biased", "abandoned": "neglected",
    "ugly": "unattractive", "crippled": "injured", "fat": "overweight", "stupid": "uninformed",
    "kill": "harm", "death": "loss", "suicide": "mental health struggle", "murder": "crime",
    "abortion": "sensitive topic", "abducted": "taken", "abduction": "kidnapping",
    "molested": "assaulted", "raped": "attacked", "pedophile": "abuser", "terrorist": "criminal",
    "assault": "attack", "violence": "conflict", "violent": "aggressive", "shot": "injured",
    "gun": "weapon", "arrested": "detained", "jail": "custody", "prison": "confinement",
    "drugs": "substances", "drug addict": "struggling with addiction", "prostitute": "sex worker",
    "incest": "inappropriate relationship", "porn": "explicit content", "nude": "unclothed",
    "naked": "exposed"
}
FLAGGED_WORDS = list(WORD_MAP.keys())

def get_uploads_playlist_id(api_key, channel_input):
    if "@" in channel_input:
        r = requests.get(f"{API_URL}/search?part=snippet&type=channel&q={channel_input}&key={api_key}")
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            return None
        channel_id = items[0]["snippet"]["channelId"]
    else:
        channel_id = channel_input.split("/")[-1]

    r = requests.get(f"{API_URL}/channels?part=contentDetails&id={channel_id}&key={api_key}")
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_video_titles_from_playlist(api_key, playlist_id, max_results=100):
    titles = []
    next_page_token = None
    while len(titles) < max_results:
        url = f"{API_URL}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={api_key}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        for item in data.get("items", []):
            title = item["snippet"]["title"]
            titles.append(title)
            if len(titles) >= max_results:
                break
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
    return titles


def scan_titles(titles, flagged_words):
    def get_word_tiers(word):
        try:
            idx = df_expanded_mapping["Flagged Keyword"].str.lower().tolist().index(word.lower())
            return (
                df_expanded_mapping.at[idx, "Less Harsh Keyword"],
                df_expanded_mapping.at[idx, "Alternative Keyword"],
                df_expanded_mapping.at[idx, "Opposite Keyword"]
            )
        except ValueError:
            return ("-", "-", "-")


    results = []
    for title in titles:
        
        matches = [word for word in flagged_words if re.search(rf"\b{re.escape(word)}\b", title, re.IGNORECASE)]
        less_harsh, alternative, opposite = [], [], []
        for word in matches:
            lh, alt, opp = get_word_tiers(word)
            less_harsh.append(lh)
            alternative.append(alt)
            opposite.append(opp)
        score = max(0, 100 - len(matches) * 10)
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(matches) if matches else "None",
            "Less Harsh Keywords": ", ".join(less_harsh) if less_harsh else "-",
            "Alternative Keywords": ", ".join(alternative) if alternative else "-",
            "Opposite Keywords": ", ".join(opposite) if opposite else "-",
            "Safety Score (100 = best)": score
        })

    return pd.DataFrame(results)

# --- Streamlit App ---
st.title("YouTube Video Title Scanner")
st.write("Scan a YouTube channel for advertiser-unfriendly words and suggest safer alternatives.")

api_key_input = st.text_input("Enter your YouTube Data API Key", type="password")
channel_input = st.text_input("Enter the YouTube Channel URL or Handle (e.g., @DharMann)")
max_titles = st.number_input("Maximum number of titles to fetch", min_value=10, max_value=500, value=100, step=10)

api_key = api_key_input if api_key_input else DEFAULT_API_KEY

if api_key and channel_input:
    playlist_id = get_uploads_playlist_id(api_key, channel_input)
    if playlist_id:
        titles = get_video_titles_from_playlist(api_key, playlist_id, max_results=max_titles)
        df_results = scan_titles(titles, FLAGGED_WORDS)
        st.dataframe(df_results)
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results as CSV", csv, "flagged_titles.csv", "text/csv")
    else:
        st.error("Could not resolve channel or playlist. Please check the URL or handle.")
