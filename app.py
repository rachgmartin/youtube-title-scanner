
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

# Full expanded keyword mapping
df_expanded_mapping = pd.DataFrame(
    "Flagged Keyword": [
        "bullied", "steals", "shamed", "poor", "forced", "scammed", "abuses", "addicted", "dumped", "hates",
        "harassed", "tormented", "shunned", "made fun of", "alienated", "ostracized", "neglected", "kill",
        "death", "suicide", "murder", "abortion", "abducted", "abduction", "molested", "raped", "pedophile",
        "terrorist", "assault", "violence", "violent", "shot", "gun", "arrested", "jail", "prison", "drugs",
        "drug addict", "prostitute", "incest", "porn", "nude", "naked", "ugly", "crippled", "fat", "stupid"
    ],
    "Less Harsh Keyword": [
        "teased", "takes", "embarrassed", "broke", "pressured", "tricked", "mistreats", "hooked", "ditched", "dislikes",
        "bothered", "troubled", "ignored", "teased", "isolated", "left out", "overlooked", "harm",
        "loss", "mental health struggle", "crime", "sensitive topic", "taken", "kidnapping", "assaulted", "attacked", "abuser",
        "criminal", "attack", "conflict", "aggressive", "injured", "weapon", "detained", "custody", "confinement", "substances",
        "struggling with addiction", "sex worker", "inappropriate relationship", "explicit content", "unclothed", "exposed", "unattractive", "injured", "overweight", "uninformed"
    ],
    "Alternative Keyword": [
        "challenged", "grabs", "insecure", "struggling", "urged", "misled", "hurts", "dependent", "left", "avoids",
        "annoyed", "unwell", "isolated", "mocked", "alone", "unwelcome", "forgotten", "injured",
        "tragedy", "struggling", "violence", "controversial", "removed", "taken", "violated", "harmed", "criminal",
        "extremist", "attack", "chaos", "hostile", "wounded", "firearm", "charged", "jailed", "imprisoned", "narcotics",
        "addiction", "worker", "taboo", "adult content", "bare", "revealing", "homely", "disabled", "large-bodied", "naive"
    ],
    "Opposite Keyword": [
        "celebrated", "gives", "proud", "wealthy", "free", "protected", "supports", "balanced", "loved", "loves",
        "respected", "peaceful", "included", "admired", "connected", "welcomed", "cared", "heal",
        "life", "hope", "justice", "choice", "safe", "home", "safe", "safe", "trusted",
        "citizen", "defended", "harmony", "calm", "healed", "safety", "freed", "released", "rehabilitated", "health",
        "recovery", "worker", "accepted", "family-friendly", "clothed", "modest", "beautiful", "able-bodied", "fit", "wise"
    ]
})


df_expanded_mapping = pd.read_csv("updated_keywords.csv")

FLAGGED_WORDS = df_expanded_mapping["Flagged Keyword"].dropna().str.lower().tolist()
