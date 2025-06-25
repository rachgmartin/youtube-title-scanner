def scan_titles_weighted(titles, flagged_words):
    def get_word_tiers(word):
        try:
            idx = df_updated_keywords["Flagged Keyword"].str.lower().tolist().index(word.lower())
            return (
                df_updated_keywords.at[idx, "Less Harsh Keyword"],
                df_updated_keywords.at[idx, "Alternative Keyword"],
                df_updated_keywords.at[idx, "Opposite Keyword"]
            )
        except ValueError:
            return ("-", "-", "-")

    def get_word_weight(word):
        return severity_weights.get(word.lower(), severity_weights["default"])

    results = []
    for title in titles:
        matches = [word for word in flagged_words if re.search(rf"\\b{re.escape(word)}\\b", title, re.IGNORECASE)]
        less_harsh, alternative, opposite = [], [], []
        penalty = 0
        for word in matches:
            lh, alt, opp = get_word_tiers(word)
            less_harsh.append(lh)
            alternative.append(alt)
            opposite.append(opp)
            penalty += get_word_weight(word)
        score = max(0, 100 - penalty)
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(matches) if matches else "None",
            "Less Harsh Keywords": ", ".join(less_harsh) if less_harsh else "-",
            "Alternative Keywords": ", ".join(alternative) if alternative else "-",
            "Opposite Keywords": ", ".join(opposite) if opposite else "-",
            "Safety Score (100 = best)": score
        })
    return pd.DataFrame(results)
