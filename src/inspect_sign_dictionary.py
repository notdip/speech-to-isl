import tarfile
import os
import json

DICT_DIR = "data/sign_dictionary"

tar_files = [f for f in os.listdir(DICT_DIR) if f.endswith(".tar")]
print(f"Found {len(tar_files)} tar shard(s): {tar_files[:3]}...")

# Inspect the first shard's contents
first_tar = os.path.join(DICT_DIR, tar_files[0])
with tarfile.open(first_tar, "r") as tar:
    members = tar.getnames()
    print(f"\nTotal files in shard: {len(members)}")
    print("First 15 entries:")
    for m in members[:15]:
        print(" ", m)

    # Find and print one actual JSON metadata file to see its structure
    json_members = [m for m in members if m.endswith(".json")]
    if json_members:
        f = tar.extractfile(json_members[0])
        data = json.load(f)
        print(f"\nSample metadata ({json_members[0]}):")
        print(json.dumps(data, indent=2))