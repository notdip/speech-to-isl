import tarfile
import json
import os
import pandas as pd

def extract_sign_dict_vocab(dict_dir="data/sign_dictionary"):
    entries = []
    tar_files = [f for f in os.listdir(dict_dir) if f.endswith(".tar")]
    for tf in tar_files:
        path = os.path.join(dict_dir, tf)
        with tarfile.open(path, "r") as tar:
            json_members = [m for m in tar.getnames() if m.endswith(".json")]
            for m in json_members:
                f = tar.extractfile(m)
                data = json.load(f)
                word = data.get("transcript", {}).get("text", "").strip().lower()
                if word:
                    base_id = m.replace(".json", "")
                    entries.append({
                        "word": word,
                        "source": "sign_dictionary",
                        "shard": tf,
                        "asset_id": base_id,
                        "video_path": f"{base_id}.mp4"
                    })
    return pd.DataFrame(entries)

def extract_cislr_vocab(cislr_dir="data/cislr"):
    csv_path = os.path.join(cislr_dir, "dataset.csv")
    df = pd.read_csv(csv_path)
    print("CISLR columns:", df.columns.tolist())
    print(df.head())
    return df

print("Extracting Sign Dictionary vocab...")
sign_dict_df = extract_sign_dict_vocab()
print(f"Sign Dictionary: {len(sign_dict_df)} entries, {sign_dict_df['word'].nunique()} unique words")
sign_dict_df.to_csv("data/sign_dict_index.csv", index=False)

print("\nExtracting CISLR vocab...")
cislr_df = extract_cislr_vocab()