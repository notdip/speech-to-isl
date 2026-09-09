import pandas as pd
import os
from gloss_translate import train_df, test_df, build_prompt, generate_ollama
import jiwer
import sacrebleu

EVAL_SIZE = 150
RESULTS_PATH = "outputs/raw_results.csv"

eval_set = test_df.sample(n=EVAL_SIZE, random_state=7).reset_index(drop=True)

if os.path.exists(RESULTS_PATH):
    results_df = pd.read_csv(RESULTS_PATH)
    print(f"Resuming — found {len(results_df)} existing rows.")
else:
    results_df = pd.DataFrame(columns=["input", "ground_truth", "llama_output", "qwen_output"])
    results_df["input"] = eval_set["text"]
    results_df["ground_truth"] = eval_set["gloss"].str.strip().str.rstrip(".").str.strip()
    results_df["llama_output"] = ""
    results_df["qwen_output"] = ""

def run_model_pass(model_name, output_col):
    print(f"\nRunning {model_name} on all rows...")
    for i, row in results_df.iterrows():
        if str(row[output_col]).strip() != "":
            continue  # already done, resume-safe
        prompt = build_prompt(row["input"], n_examples=8)
        out = generate_ollama(prompt, model=model_name)
        results_df.at[i, output_col] = out.strip().rstrip(".").strip()
        if i % 20 == 0:
            print(f"  {i}/{len(results_df)}")
            results_df.to_csv(RESULTS_PATH, index=False)
    results_df.to_csv(RESULTS_PATH, index=False)

run_model_pass("llama3.1:8b", "llama_output")
run_model_pass("qwen2.5:7b", "qwen_output")

print("Done. Saved to", RESULTS_PATH)

# --- Metrics ---
def token_accuracy(pred, truth):
    pred_tokens, truth_tokens = pred.split(), truth.split()
    matches = sum(1 for p, t in zip(pred_tokens, truth_tokens) if p == t)
    return matches / max(len(truth_tokens), 1)

def compute_metrics(df, col, label):
    valid = df[df[col].astype(str).str.strip() != ""]
    preds, truths = valid[col].tolist(), valid["ground_truth"].tolist()
    accs = [token_accuracy(p, t) for p, t in zip(preds, truths)]
    avg_acc = sum(accs) / len(accs)
    wer_scores = [jiwer.wer(t, p) for p, t in zip(preds, truths)]
    avg_edit = sum(wer_scores) / len(wer_scores)
    bleu = sacrebleu.corpus_bleu(preds, [truths]).score
    chrf = sacrebleu.corpus_chrf(preds, [truths]).score
    print(f"\n--- {label} (n={len(valid)}) ---")
    print(f"Token Accuracy: {avg_acc:.4f} | Edit Distance: {avg_edit:.4f} | BLEU: {bleu:.2f} | ChrF: {chrf:.2f}")
    return {"model": label, "n": len(valid), "token_accuracy": avg_acc, "edit_distance": avg_edit, "bleu": bleu, "chrf": chrf}

llama_metrics = compute_metrics(results_df, "llama_output", "Llama 3.1 8B")
qwen_metrics = compute_metrics(results_df, "qwen_output", "Qwen2.5 7B")

pd.DataFrame([llama_metrics, qwen_metrics]).to_csv("outputs/comparison_table.csv", index=False)
print("\nSaved comparison table to outputs/comparison_table.csv")