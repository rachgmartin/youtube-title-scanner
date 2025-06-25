
import streamlit as st
import pandas as pd
import requests
import os
import re
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
DEFAULT_API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- CONFIG ---
API_URL = "https://www.googleapis.com/youtube/v3"

# --- WORD MAPPING ---
WORD_MAP = {
    "bullied": "teased",
    "shamed": "judged",
    "abuses": "mistreats",
    "scammed": "misled",
    "addicted": "struggling",
    "dumped": "left",
    "hates": "dislikes",
    "harassed": "bothered",
    "revenge": "gets even",
    "regret": "rethink",
    "toxic": "controlling",
    "worst": "challenging",
    "evil": "unfair",
    "cheating": "dishonest",
    "racist": "biased",
    "abandoned": "neglected",
    "ugly": "unattractive",
    "crippled": "injured",
    "fat": "overweight",
    "stupid": "uninformed",
    "kill": "harm",
    "death": "loss",
    "suicide": "mental health struggle",
    "murder": "crime",
    "abortion": "sensitive topic",
    "abducted": "taken",
    "abduction": "kidnapping",
    "molested": "assaulted",
    "raped": "attacked",
    "pedophile": "abuser",
    "terrorist": "criminal",
    "assault": "attack",
    "violence": "conflict",
    "violent": "aggressive",
    "shot": "injured",
    "gun": "weapon",
    "arrested": "detained",
    "jail": "custody",
    "prison": "confinement",
    "drugs": "substances",
    "drug addict": "struggling with addiction",
    "prostitute": "sex worker",
    "incest": "inappropriate relationship",
    "porn": "explicit content",
    "nude": "unclothed",
    "naked": "exposed"
}

FLAGGED_WORDS = list(WORD_MAP.keys())

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

def get_video_titles(api_key, channel_id, max_results=100):
    titles = []
    url = f"{API_URL}/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=50"
    next_page_token = None

    while len(titles) < max_results:
        paginated_url = url + (f"&pageToken={next_page_token}" if next_page_token else "")
        response = requests.get(paginated_url)
        data = response.json()
        for item in data.get("items", []):
            if item["id"].get("videoId"):
                title = item["snippet"]["title"]
                titles.append(title)
                if len(titles) >= max_results:
                    break
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
    return titles

def scan_titles(titles, flagged_words):
    results = []
    for title in titles:
        matches = [word for word in flagged_words if re.search(rf"\b{re.escape(word)}\b", title, re.IGNORECASE)]
        suggestions = [WORD_MAP[word] for word in matches]
        score = max(0, 100 - len(matches) * 10)
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(matches) if matches else "None",
            "Suggested Alternatives": ", ".join(suggestions) if suggestions else "-",
            "Safety Score (100 = best)": score
        })
    return pd.DataFrame(results)

# --- STREAMLIT UI ---
st.title("YouTube Video Title Scanner")
st.write("Scan a YouTube channel for flagged keywords, see safer suggestions, and score titles.")

api_key_input = st.text_input("Enter your YouTube Data API Key", type="password")
channel_input = st.text_input("Enter the YouTube Channel URL or Handle (e.g., @DharMann)")
max_titles = st.number_input("Maximum number of titles to fetch", min_value=10, max_value=500, value=100, step=10)

api_key = api_key_input if api_key_input else DEFAULT_API_KEY

if api_key and channel_input:
    channel_id = get_channel_id(api_key, channel_input)
    if channel_id:
        titles = get_video_titles(api_key, channel_id, max_results=max_titles)
        df_results = scan_titles(titles, FLAGGED_WORDS)
        st.dataframe(df_results)

        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results as CSV", csv, "flagged_titles.csv", "text/csv")
    else:
        st.error("Could not find a valid channel ID. Check the URL or handle and try again.")
