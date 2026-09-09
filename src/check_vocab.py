import tarfile
import os
import json
import random

DICT_DIR = "data/sign_dictionary"
tar_files = [f for f in os.listdir(DICT_DIR) if f.endswith(".tar")]

all_words = []
for tf in tar_files:
    path = os.path.join(DICT_DIR, tf)
    with tarfile.open(path, "r") as tar:
        json_members = [m for m in tar.getnames() if m.endswith(".json")]
        sample = random.sample(json_members, min(40, len(json_members)))
        for m in sample:
            f = tar.extractfile(m)
            data = json.load(f)
            word = data.get("transcript", {}).get("text", "")
            all_words.append(word)

print(f"Sampled {len(all_words)} words across {len(tar_files)} shards")
print("\nRandom sample of 60:")
print(sorted(random.sample(all_words, min(60, len(all_words)))))