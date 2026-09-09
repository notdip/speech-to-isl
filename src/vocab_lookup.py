import pandas as pd
import os
from rapidfuzz import fuzz, process

# --- Paths ---
CISLR_VIDEO_DIR = "data/cislr/CISLR_v1.5-a_videos/CISLR_v1.5-a_videos"
SIGN_DICT_DIR = "data/sign_dictionary"

# --- Load both vocab sources ---
cislr_df = pd.read_csv("data/cislr/dataset.csv")
cislr_df["gloss"] = cislr_df["gloss"].str.strip().str.lower()

sign_dict_df = pd.read_csv("data/sign_dict_index.csv")
sign_dict_df["word"] = sign_dict_df["word"].str.strip().str.lower()

# --- Build unified lookup: word -> (source, asset reference) ---
cislr_lookup = {}
for _, row in cislr_df.iterrows():
    word = row["gloss"]
    if word not in cislr_lookup:
        cislr_lookup[word] = {"source": "cislr", "uid": row["uid"], "category": row["category"]}

sign_dict_lookup = {}
for _, row in sign_dict_df.iterrows():
    word = row["word"]
    if word not in sign_dict_lookup:
        sign_dict_lookup[word] = {"source": "sign_dictionary", "asset_id": row["asset_id"], "shard": row["shard"]}

all_words_cislr = list(cislr_lookup.keys())
all_words_sign_dict = list(sign_dict_lookup.keys())

def lookup_word(word, fuzzy_threshold=85):
    word = word.strip().lower()

    if word in cislr_lookup:
        return {"matched_word": word, "match_type": "exact", **cislr_lookup[word]}

    if word in sign_dict_lookup:
        return {"matched_word": word, "match_type": "exact", **sign_dict_lookup[word]}

    result = process.extractOne(word, all_words_cislr, scorer=fuzz.ratio)
    if result and result[1] >= fuzzy_threshold:
        matched_word = result[0]
        return {"matched_word": matched_word, "match_type": "fuzzy", "score": result[1], **cislr_lookup[matched_word]}

    result = process.extractOne(word, all_words_sign_dict, scorer=fuzz.ratio)
    if result and result[1] >= fuzzy_threshold:
        matched_word = result[0]
        return {"matched_word": matched_word, "match_type": "fuzzy", "score": result[1], **sign_dict_lookup[matched_word]}

    return {"matched_word": word, "match_type": "fingerspell", "source": "fingerspelling"}

def get_video_path(match_result):
    """Resolve a lookup_word() result into an actual file path (CISLR only — Sign Dictionary needs extraction)."""
    if match_result["source"] == "cislr":
        return os.path.join(CISLR_VIDEO_DIR, f"{match_result['uid']}.mp4")
    elif match_result["source"] == "sign_dictionary":
        return {"shard": match_result["shard"], "asset_id": match_result["asset_id"]}
    else:
        return None

if __name__ == "__main__":
    print(f"CISLR vocab: {len(cislr_lookup)} words | Sign Dictionary vocab: {len(sign_dict_lookup)} words")

    test_words = ["school", "tomorrow", "go", "quantum", "education", "happy", "amnon"]
    for w in test_words:
        result = lookup_word(w)
        print(f"'{w}' -> {result}")