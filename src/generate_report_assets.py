import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from collections import Counter
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
from vocab_lookup import lookup_word

import numpy as np
import jiwer
import sacrebleu

os.makedirs("outputs/report_assets", exist_ok=True)

df = pd.read_csv("outputs/raw_results.csv")


def align_tokens(pred, truth):
    """Position-based alignment, same convention as the accuracy metric already used in evaluate.py."""
    pred_tokens = str(pred).split()
    truth_tokens = str(truth).split()

    n = max(len(pred_tokens), len(truth_tokens))

    pred_tokens += [""] * (n - len(pred_tokens))
    truth_tokens += [""] * (n - len(truth_tokens))

    return pred_tokens, truth_tokens


def build_confusion_data(model_col, top_k=15):
    all_true, all_pred = [], []

    for _, row in df.iterrows():
        p, t = align_tokens(row[model_col], row["ground_truth"])
        all_true.extend(t)
        all_pred.extend(p)

    # Determine top-K most frequent ground-truth tokens; bucket the rest as OTHER
    freq = Counter([t for t in all_true if t])

    top_tokens = set([tok for tok, _ in freq.most_common(top_k)])

    def bucket(tok):
        if tok == "":
            return "∅"
        return tok if tok in top_tokens else "OTHER"

    true_buckets = [bucket(t) for t in all_true]
    pred_buckets = [bucket(p) for p in all_pred]

    labels = sorted(set(true_buckets) | set(pred_buckets))

    cm = confusion_matrix(
        true_buckets,
        pred_buckets,
        labels=labels
    )

    return cm, labels


def plot_confusion_matrix(cm, labels, title, filename):
    plt.figure(figsize=(10, 8))

    sns.heatmap(
        cm,
        xticklabels=labels,
        yticklabels=labels,
        annot=True,
        fmt="d",
        cmap="magma",
        cbar=True
    )

    plt.xlabel("Predicted")
    plt.ylabel("Ground Truth")
    plt.title(title)

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()

    plt.savefig(
        f"outputs/report_assets/{filename}",
        dpi=150
    )

    plt.close()

    print(f"Saved {filename}")


# ============================================================
# 1. CONFUSION MATRICES
# ============================================================

for model_col, model_name in [
    ("llama_output", "Llama 3.1 8B"),
    ("qwen_output", "Qwen2.5 7B")
]:

    cm, labels = build_confusion_data(model_col)

    plot_confusion_matrix(
        cm,
        labels,
        f"Gloss Token Confusion Matrix — {model_name}",
        f"confusion_matrix_{model_col}.png"
    )

    # ---- TERMINAL OUTPUT ----
    print("\n" + "=" * 70)
    print(f"CONFUSION MATRIX — {model_name}")
    print("=" * 70)

    print("\nLabels:")
    print(labels)

    print("\nMatrix:")
    print(pd.DataFrame(
        cm,
        index=[f"GT:{x}" for x in labels],
        columns=[f"PRED:{x}" for x in labels]
    ).to_string())


# ============================================================
# 2. COMPARISON OF ALL FOUR METRICS
# ============================================================

comparison_df = pd.read_csv("outputs/comparison_table.csv")

metrics = [
    "token_accuracy",
    "edit_distance",
    "bleu",
    "chrf"
]

fig, axes = plt.subplots(
    1,
    4,
    figsize=(18, 4)
)

for ax, metric in zip(axes, metrics):

    ax.bar(
        comparison_df["model"],
        comparison_df[metric],
        color=["#534AB7", "#1D9E75"]
    )

    ax.set_title(
        metric.replace("_", " ").title()
    )

    ax.tick_params(
        axis="x",
        rotation=15
    )

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/metric_comparison.png",
    dpi=150
)

plt.close()

print("Saved metric_comparison.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("OVERALL MODEL COMPARISON")
print("=" * 70)

print(
    comparison_df[
        ["model", "token_accuracy", "edit_distance", "bleu", "chrf"]
    ].to_string(index=False)
)


# ============================================================
# 3. TOP CONFUSED WORD PAIRS
# ============================================================

def top_confused_pairs(model_col, n=15):

    pairs = Counter()

    for _, row in df.iterrows():

        p, t = align_tokens(
            row[model_col],
            row["ground_truth"]
        )

        for pt, tt in zip(p, t):

            if pt != tt and tt != "":
                pairs[(tt, pt)] += 1

    return pairs.most_common(n)


for model_col, model_name in [
    ("llama_output", "Llama 3.1 8B"),
    ("qwen_output", "Qwen2.5 7B")
]:

    print("\n" + "=" * 70)
    print(f"TOP CONFUSED PAIRS — {model_name}")
    print("(ground_truth -> predicted)")
    print("=" * 70)

    confused = top_confused_pairs(model_col)

    for rank, ((true_tok, pred_tok), count) in enumerate(
        confused,
        start=1
    ):
        print(
            f"{rank:2}. {true_tok!r} -> {pred_tok!r}: {count}x"
        )


# ============================================================
# 4. PER-SENTENCE SCORE DISTRIBUTIONS
# ============================================================

def per_sentence_scores(model_col):

    scores = []

    for _, row in df.iterrows():

        pred = str(row[model_col])
        truth = str(row["ground_truth"])

        bleu = sacrebleu.sentence_bleu(
            pred,
            [truth]
        ).score

        wer = (
            jiwer.wer(truth, pred)
            if pred
            else 1.0
        )

        scores.append({
            "bleu": bleu,
            "edit_distance": wer
        })

    return pd.DataFrame(scores)


llama_scores = per_sentence_scores(
    "llama_output"
)

qwen_scores = per_sentence_scores(
    "qwen_output"
)


fig, axes = plt.subplots(
    1,
    2,
    figsize=(12, 5)
)

axes[0].boxplot(
    [
        llama_scores["bleu"],
        qwen_scores["bleu"]
    ],
    tick_labels=[
        "Llama 3.1 8B",
        "Qwen2.5 7B"
    ]
)

axes[0].set_title(
    "BLEU Score Distribution (per sentence)"
)


axes[1].boxplot(
    [
        llama_scores["edit_distance"],
        qwen_scores["edit_distance"]
    ],
    tick_labels=[
        "Llama 3.1 8B",
        "Qwen2.5 7B"
    ]
)

axes[1].set_title(
    "Edit Distance Distribution (per sentence)"
)

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/score_distributions.png",
    dpi=150
)

plt.close()

print("Saved score_distributions.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("PER-SENTENCE SCORE STATISTICS")
print("=" * 70)

for name, scores in [
    ("Llama 3.1 8B", llama_scores),
    ("Qwen2.5 7B", qwen_scores)
]:

    print(f"\n{name}")

    print("-" * 50)

    print(
        f"BLEU:"
        f"\n  Mean   : {scores['bleu'].mean():.4f}"
        f"\n  Median : {scores['bleu'].median():.4f}"
        f"\n  Min    : {scores['bleu'].min():.4f}"
        f"\n  Max    : {scores['bleu'].max():.4f}"
        f"\n  Std    : {scores['bleu'].std():.4f}"
    )

    print(
        f"\nEdit Distance / WER:"
        f"\n  Mean   : {scores['edit_distance'].mean():.4f}"
        f"\n  Median : {scores['edit_distance'].median():.4f}"
        f"\n  Min    : {scores['edit_distance'].min():.4f}"
        f"\n  Max    : {scores['edit_distance'].max():.4f}"
        f"\n  Std    : {scores['edit_distance'].std():.4f}"
    )


# ============================================================
# 5. SENTENCE LENGTH VS ACCURACY
# ============================================================

df["input_len"] = (
    df["input"]
    .str.split()
    .str.len()
)

df["llama_bleu"] = llama_scores["bleu"]
df["qwen_bleu"] = qwen_scores["bleu"]


plt.figure(figsize=(8, 6))

plt.scatter(
    df["input_len"],
    df["llama_bleu"],
    alpha=0.5,
    label="Llama 3.1 8B",
    color="#534AB7"
)

plt.scatter(
    df["input_len"],
    df["qwen_bleu"],
    alpha=0.5,
    label="Qwen2.5 7B",
    color="#1D9E75"
)

plt.xlabel("Input Sentence Length (words)")
plt.ylabel("BLEU Score")
plt.title("Sentence Length vs Translation Quality")

plt.legend()

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/length_vs_accuracy.png",
    dpi=150
)

plt.close()

print("Saved length_vs_accuracy.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("SENTENCE LENGTH VS BLEU")
print("=" * 70)

print(
    f"\nInput sentence length:"
    f"\n  Mean   : {df['input_len'].mean():.2f}"
    f"\n  Median : {df['input_len'].median():.2f}"
    f"\n  Min    : {df['input_len'].min()}"
    f"\n  Max    : {df['input_len'].max()}"
)

print("\nCorrelation with BLEU:")

print(
    f"  Llama 3.1 8B : "
    f"{df['input_len'].corr(df['llama_bleu']):.4f}"
)

print(
    f"  Qwen2.5 7B   : "
    f"{df['input_len'].corr(df['qwen_bleu']):.4f}"
)


# ============================================================
# 6. VOCABULARY COVERAGE
# ============================================================

all_gt_tokens = (
    " ".join(
        df["ground_truth"].astype(str)
    )
    .split()
)

source_counts = Counter()

for tok in all_gt_tokens:

    clean = (
        tok
        .replace("DESC-", "")
        .replace("X-", "")
        .strip()
        .lower()
    )

    if not clean:
        continue

    match = lookup_word(clean)

    source_counts[
        match["source"]
    ] += 1


plt.figure(figsize=(6, 6))

plt.pie(
    source_counts.values(),
    labels=source_counts.keys(),
    autopct="%1.1f%%",
    colors=[
        "#534AB7",
        "#1D9E75",
        "#E8A33D"
    ]
)

plt.title(
    "Vocabulary Coverage: "
    "Where Gloss Tokens Are Resolved From"
)

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/vocab_coverage.png",
    dpi=150
)

plt.close()

print("Saved vocab_coverage.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("VOCABULARY COVERAGE")
print("=" * 70)

total_vocab = sum(source_counts.values())

for source, count in source_counts.most_common():

    percentage = (
        count / total_vocab * 100
        if total_vocab
        else 0
    )

    print(
        f"{source:<25} "
        f"{count:>8} tokens "
        f"({percentage:6.2f}%)"
    )

print(f"\nTotal resolved tokens: {total_vocab}")


# ============================================================
# 7. DATASET SCALE COMPARISON
# ============================================================

dataset_sizes = {
    "ASLG-PC12\n(gloss pairs)": 85955 + 1755,
    "CISLR\n(word vocab)": 4765,
    "Sign Dictionary\n(word vocab)": 3095,
    "iSign\n(sentences)": 127237,
}


plt.figure(figsize=(8, 5))

plt.bar(
    dataset_sizes.keys(),
    dataset_sizes.values(),
    color="#534AB7"
)

plt.ylabel("Count (log scale)")
plt.yscale("log")
plt.title("Dataset Scale Comparison")

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/dataset_scale.png",
    dpi=150
)

plt.close()

print("Saved dataset_scale.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("DATASET SCALE")
print("=" * 70)

for dataset, size in dataset_sizes.items():

    clean_name = (
        dataset
        .replace("\n", " ")
    )

    print(
        f"{clean_name:<35} : {size:,}"
    )


# ============================================================
# 8. DESC- PREFIX HANDLING ACCURACY
# ============================================================

def desc_accuracy(model_col):

    desc_correct = 0
    desc_total = 0

    plain_correct = 0
    plain_total = 0

    for _, row in df.iterrows():

        pred_tokens = str(
            row[model_col]
        ).split()

        truth_tokens = str(
            row["ground_truth"]
        ).split()

        for i, t in enumerate(truth_tokens):

            p = (
                pred_tokens[i]
                if i < len(pred_tokens)
                else ""
            )

            if t.startswith("DESC-"):

                desc_total += 1

                if p == t:
                    desc_correct += 1

            else:

                plain_total += 1

                if p == t:
                    plain_correct += 1

    desc_acc = (
        desc_correct / max(desc_total, 1)
    )

    plain_acc = (
        plain_correct / max(plain_total, 1)
    )

    return (
        desc_acc,
        plain_acc,
        desc_correct,
        desc_total,
        plain_correct,
        plain_total
    )


fig, ax = plt.subplots(
    figsize=(7, 5)
)

x = np.arange(2)
width = 0.35


for i, (col, name) in enumerate([
    ("llama_output", "Llama 3.1 8B"),
    ("qwen_output", "Qwen2.5 7B")
]):

    desc_acc, plain_acc, _, _, _, _ = desc_accuracy(col)

    ax.bar(
        x + i * width,
        [desc_acc, plain_acc],
        width,
        label=name
    )


ax.set_xticks(
    x + width / 2
)

ax.set_xticklabels([
    "DESC- tokens",
    "Plain tokens"
])

ax.set_ylabel(
    "Token Accuracy"
)

ax.set_title(
    "Accuracy: DESC-Prefixed vs Plain Gloss Tokens"
)

ax.legend()

plt.tight_layout()

plt.savefig(
    "outputs/report_assets/desc_prefix_accuracy.png",
    dpi=150
)

plt.close()

print("Saved desc_prefix_accuracy.png")


# ---- TERMINAL OUTPUT ----

print("\n" + "=" * 70)
print("DESC- PREFIX HANDLING ACCURACY")
print("=" * 70)

for col, name in [
    ("llama_output", "Llama 3.1 8B"),
    ("qwen_output", "Qwen2.5 7B")
]:

    (
        desc_acc,
        plain_acc,
        desc_correct,
        desc_total,
        plain_correct,
        plain_total
    ) = desc_accuracy(col)

    print(f"\n{name}")
    print("-" * 50)

    print(
        f"DESC- tokens:"
        f"\n  Correct : {desc_correct:,}"
        f"\n  Total   : {desc_total:,}"
        f"\n  Accuracy: {desc_acc:.4%}"
    )

    print(
        f"\nPlain tokens:"
        f"\n  Correct : {plain_correct:,}"
        f"\n  Total   : {plain_total:,}"
        f"\n  Accuracy: {plain_acc:.4%}"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print("\nGenerated report assets:")

for filename in sorted(
    os.listdir("outputs/report_assets")
):

    print(f"  ✓ {filename}")

print("\n")