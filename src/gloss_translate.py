import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# --- Load & split data ---
DATA_PATH = "data/aslg_pc12/train.csv"

df = pd.read_csv(DATA_PATH)
df["gloss"] = df["gloss"].str.strip()
df["text"] = df["text"].str.strip()

from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(df, test_size=0.02, random_state=42)

print(f"Train pool: {len(train_df)} | Test set: {len(test_df)}")

# --- Few-shot prompt builder ---
def get_few_shot_examples(n=8, seed=None):
    # Bias sampling toward examples containing DESC- to teach that pattern explicitly
    desc_examples = train_df[train_df["gloss"].str.contains("DESC-", na=False)]
    n_desc = min(3, len(desc_examples))
    sample_desc = desc_examples.sample(n=n_desc, random_state=seed)
    sample_rest = train_df.sample(n=n - n_desc, random_state=seed)
    sample = pd.concat([sample_desc, sample_rest]).sample(frac=1, random_state=seed)  # shuffle

    examples = ""
    for _, row in sample.iterrows():
        examples += f"English: {row['text']}\nGloss: {row['gloss']}\n\n"
    return examples

# Words that are grammatically valid English but carry no independent sign in ISL gloss —
# these should be dropped even if the LLM leaves them in.
DROPPABLE_TOKENS = {"am", "is", "are", "was", "were", "be", "been", "being", "a", "an", "the"}

def clean_gloss(gloss_text):
    tokens = gloss_text.split()
    cleaned = [t for t in tokens if t.lower().strip(".,!?") not in DROPPABLE_TOKENS]
    return " ".join(cleaned)

def build_prompt(input_sentence, n_examples=8, seed=42):
    examples = get_few_shot_examples(n_examples, seed=seed)
    prompt = f"""You are a sign language gloss translator. Convert English sentences into gloss notation following these rules observed in the examples:
- Use uppercase words
- Drop articles (a, an, the) and most linking/auxiliary verbs (is, am, are, was)
- Use the DESC- prefix for descriptive/adjectival modifiers, exactly as shown in the examples
- Use American English spelling (e.g. PROGRAM not PROGRAMME)
- Keep word order close to topic-comment structure
- Output ONLY the gloss line, nothing else — no explanations

Examples:
{examples}Now convert this sentence:
English: {input_sentence}
Gloss:"""
    return prompt

# --- Ollama backend (supports any locally pulled model) ---
def generate_ollama(prompt, model="llama3.1:8b"):
    import ollama
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

if __name__ == "__main__":
    # Quick manual test — confirms this module works standalone
    test_sentence = test_df.iloc[0]["text"]
    ground_truth = test_df.iloc[0]["gloss"]
    prompt = build_prompt(test_sentence)

    print(f"\nInput: {test_sentence}")
    print(f"Ground truth gloss: {ground_truth}")
    print(f"Llama 3.1 8B output: {generate_ollama(prompt, model='llama3.1:8b')}")
    print(f"Qwen2.5 7B output: {generate_ollama(prompt, model='qwen2.5:7b')}")