import streamlit as st
import pandas as pd
import re
import requests
from io import BytesIO

# Define flagged keywords and metadata
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

# Title
st.title("YouTube Video Title Scanner")

# Inputs
api_key = st.text_input("Enter your YouTube Data API Key", type="password")
channel_id = st.text_input("Enter the YouTube Channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)")
max_results = st.number_input("Maximum number of titles to fetch", min_value=10, max_value=500, value=100)

# Fetch titles using pagination
def fetch_video_titles(api_key, channel_id, max_results):
    titles = []
    page_token = ""
    while len(titles) < max_results:
        url = (
            f"https://www.googleapis.com/youtube/v3/search?key={api_key}"
            f"&channelId={channel_id}&part=snippet,id&order=date&maxResults=50&type=video"
            + (f"&pageToken={page_token}" if page_token else "")
        )
        response = requests.get(url)
        data = response.json()
        for item in data.get("items", []):
            if "title" in item["snippet"]:
                titles.append(item["snippet"]["title"])
                if len(titles) >= max_results:
                    break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return titles

# Analyze titles
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

# Button to run scanner
if st.button("Scan Titles") and api_key and channel_id:
    st.info("Fetching video titles...")
    titles = fetch_video_titles(api_key, channel_id, max_results)
    df = analyze_titles(titles)
    st.success("Scan complete!")
    st.dataframe(df)

    # Excel download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Scan Results')
    st.download_button("Download Excel File", data=output.getvalue(), file_name="title_scan_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

