import pandas as pd
import random

df = pd.read_csv('data/aslg_pc12/train.csv')
df['gloss'] = df['gloss'].str.strip()
df['text'] = df['text'].str.strip()

def get_few_shot_examples(n=5, seed=None):
    sample = df.sample(n=n, random_state=seed)
    examples = ""
    for _, row in sample.iterrows():
        examples += f"English: {row['text']}\nGloss: {row['gloss']}\n\n"
    return examples

def build_prompt(input_sentence, n_examples=5):
    examples = get_few_shot_examples(n_examples)
    prompt = f"""You are a sign language gloss translator. Convert English sentences into gloss notation by following these rules observed in the examples: use uppercase words, drop articles (a, an, the) and most prepositions, keep word order close to topic-comment structure, and compress descriptive phrases where natural.

Examples:
{examples}Now convert this sentence:
English: {input_sentence}
Gloss:"""
    return prompt

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

test_sentence = "I am going to school tomorrow"
prompt = build_prompt(test_sentence)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)