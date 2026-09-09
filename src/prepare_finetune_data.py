import pandas as pd
import json

df = pd.read_csv("data/aslg_pc12/train.csv")
df["gloss"] = df["gloss"].str.strip()
df["text"] = df["text"].str.strip()

from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(df, test_size=0.02, random_state=42)  # same split as before — keep test set untouched

# Subsample for a tractable training run — 20k is plenty of signal for this task
train_subset = train_df.sample(n=20000, random_state=42)

INSTRUCTION = "Convert this English sentence into sign language gloss notation (uppercase, using DESC- for descriptive modifiers, dropping articles and auxiliary verbs)."

with open("data/finetune_data.jsonl", "w", encoding="utf-8") as f:
    for _, row in train_subset.iterrows():
        entry = {
            "instruction": INSTRUCTION,
            "input": row["text"],
            "output": row["gloss"]
        }
        f.write(json.dumps(entry) + "\n")

print(f"Wrote {len(train_subset)} training examples to data/finetune_data.jsonl")