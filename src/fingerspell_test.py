import tempfile
from vocab_lookup import lookup_word
from assemble_video import get_fingerspell_clips

# Force a word we know needs fingerspelling
test_word = "quantum"
match = lookup_word(test_word)
print(f"Lookup result: {match}")

with tempfile.TemporaryDirectory() as temp_dir:
    clips = get_fingerspell_clips(test_word, temp_dir)
    print(f"Generated {len(clips)} fingerspell clips:")
    for c in clips:
        import os
        print(f"  {c} (exists: {os.path.exists(c)}, size: {os.path.getsize(c) if os.path.exists(c) else 'N/A'})")

from pipeline import full_pipeline_from_text
full_pipeline_from_text("The xenolith i saw with my eyes was quixotic")