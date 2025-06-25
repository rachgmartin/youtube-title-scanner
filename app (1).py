
import streamlit as st
import pandas as pd
import requests
import re
from io import BytesIO

# Example flagged keywords and mapping
FLAGGED_WORDS = [
    {"Flagged Keyword": "scam", "Less Harsh": "scheme", "Alternative": "trick", "Severity": 0.9},
    {"Flagged Keyword": "killed", "Less Harsh": "hurt", "Alternative": "taken down", "Severity": 0.95},
    {"Flagged Keyword": "sex", "Less Harsh": "affair", "Alternative": "intimacy", "Severity": 0.98},
    {"Flagged Keyword": "addicted", "Less Harsh": "dependent", "Alternative": "hooked", "Severity": 0.85},
    # Add more mappings as needed...
]

def fetch_video_titles(api_key, channel_id, max_results):
    titles = []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 50,
        "type": "video"
    }
    total_fetched = 0
    while url and total_fetched < max_results:
        response = requests.get(url, params=params).json()
        items = response.get("items", [])
        for item in items:
            title = item["snippet"]["title"]
            titles.append(title)
            total_fetched += 1
            if total_fetched >= max_results:
                break
        url = f"https://www.googleapis.com/youtube/v3/search?pageToken={response.get('nextPageToken')}" if response.get("nextPageToken") else None
    return titles

def scan_titles(titles, flagged_list):
    df = pd.DataFrame(titles, columns=["Video Title"])
    flagged_data = []

    for title in df["Video Title"]:
        found_keywords = []
        less_harsh = []
        alternative = []
        score = 100
        for word in flagged_list:
            if re.search(rf"\b{word['Flagged Keyword']}\b", title, re.IGNORECASE):
                found_keywords.append(word['Flagged Keyword'])
                less_harsh.append(word['Less Harsh'])
                alternative.append(word['Alternative'])
                score -= word['Severity'] * 20
        flagged_data.append({
            "Video Title": title,
            "Flagged Words": ", ".join(found_keywords) if found_keywords else "None",
            "Less Harsh Keywords": ", ".join(less_harsh) if less_harsh else "-",
            "Alternative Keywords": ", ".join(alternative) if alternative else "-",
            "Safety Score": max(0, round(score, 1))
        })
    return pd.DataFrame(flagged_data)

st.title("YouTube Video Title Scanner")
st.markdown("Scan a YouTube channel for advertiser-unfriendly words and suggest safer alternatives.")

api_key = st.text_input("Enter your YouTube Data API Key", type="password")
channel_id = st.text_input("Enter the YouTube Channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)")
max_results = st.number_input("Maximum number of titles to fetch", min_value=10, max_value=500, step=10, value=100)

if st.button("Scan Titles") and api_key and channel_id:
    try:
        st.info("Fetching video titles...")
        titles = fetch_video_titles(api_key, channel_id, int(max_results))
        df_results = scan_titles(titles, FLAGGED_WORDS)
        st.success("Scan complete!")
        st.dataframe(df_results)

        output = BytesIO()
        df_results.to_excel(output, index=False, engine='xlsxwriter')
        st.download_button(
            label="Download Results as Excel",
            data=output.getvalue(),
            file_name="title_scan_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Something went wrong: {e}")
