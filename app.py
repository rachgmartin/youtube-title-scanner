import streamlit as st
import pandas as pd
import re
import requests
from io import BytesIO

FLAGGED_WORDS = {
    "kill": ("harm", "remove", "end"),
    "scam": ("mislead", "trick", "fraud"),
    "sex": ("intimacy", "romance", "relationship"),
    "abuse": ("mistreat", "harm", "neglect"),
    "addicted": ("dependent", "hooked", "struggling"),
    "toxic": ("unhealthy", "challenging", "hostile"),
    "revenge": ("payback", "retaliation", "justice"),
    "bullied": ("teased", "targeted", "ostracized"),
    "steals": ("takes", "snatches", "grabs"),
    "shamed": ("embarrassed", "exposed", "humiliated"),
    "poor": ("struggling", "broke", "underprivileged"),
    "forced": ("compelled", "obliged", "pushed"),
    "scammed": ("tricked", "deceived", "conned"),
    "abuses": ("mistreats", "harms", "violates"),
    "dumped": ("left", "rejected", "split"),
    "hates": ("dislikes", "resents", "loathes"),
    "harassed": ("bothered", "pestered", "tormented"),
    "tormented": ("troubled", "disturbed", "haunted"),
    "shunned": ("avoided", "ignored", "rejected"),
    "alienated": ("isolated", "excluded", "distanced"),
    "ostracized": ("banished", "excluded", "shunned"),
    "neglected": ("ignored", "overlooked", "abandoned")
}

st.title("YouTube Video Title Scanner")

api_key = st.text_input("Enter your YouTube Data API Key", type="password")
channel_id = st.text_input("Enter the YouTube Channel ID")
max_results = st.number_input("Maximum number of titles to fetch", min_value=10, max_value=500, value=100)

def get_video_ids(api_key, channel_id, max_results):
    video_ids = []
    page_token = ""
    while len(video_ids) < max_results:
        url = (
            f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}"
            f"&part=id&order=date&maxResults=50&type=video"
            + (f"&pageToken={page_token}" if page_token else "")
        )
        res = requests.get(url)
        data = res.json()
        for item in data.get("items", []):
            video_ids.append(item["id"]["videoId"])
            if len(video_ids) >= max_results:
                break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return video_ids

def get_video_titles(api_key, video_ids):
    titles = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        url = (
            f"https://www.googleapis.com/youtube/v3/videos?key={api_key}"
            f"&id={','.join(batch_ids)}&part=snippet"
        )
        res = requests.get(url)
        data = res.json()
        for item in data.get("items", []):
            titles.append(item["snippet"]["title"])
    return titles

def analyze_titles(titles):
    results = []
    for title in titles:
        flagged = []
        less_harsh = []
        alternatives = []
        for word, (less, *alts) in FLAGGED_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", title, re.IGNORECASE):
                flagged.append(word)
                less_harsh.append(less)
                alternatives.append(", ".join(alts))
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(flagged) if flagged else "None",
            "Less Harsh Keywords": ", ".join(less_harsh) if less_harsh else "-",
            "Alternative Keywords": ", ".join(alternatives) if alternatives else "-"
        })
    return pd.DataFrame(results)

if st.button("Scan Titles") and api_key and channel_id:
    st.info("Fetching video titles...")
    video_ids = get_video_ids(api_key, channel_id, max_results)
    titles = get_video_titles(api_key, video_ids)
    df = analyze_titles(titles)
    st.success("Scan complete!")
    st.dataframe(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Scan Results')
    st.download_button("Download Excel File", data=output.getvalue(), file_name="title_scan_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


