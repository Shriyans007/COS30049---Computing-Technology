import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# CONFIG 
DATA_PATH = os.environ.get(
    "DATA_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "processed", "final_dataset.csv",
    )
)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

FEATURES = [
    "char_count", "word_count", "avg_word_len", "vocab_div_ratio",
    "complex_word_ratio", "stopword_ratio", "upper_letter_ratio",
    "semicolon_dash_count", "char_entropy", "rep_bigram",
    "ai_tell_count", "doc_pos",
]

# LOAD 
print(f"Loading {DATA_PATH}")
df = pd.read_csv(DATA_PATH)



# Feature Stats 

means = df.groupby("label")[FEATURES].mean().T
means.columns = ["human_mean", "ai_mean"]
stds = df.groupby("label")[FEATURES].std().T
stds.columns = ["human_std", "ai_std"]
flat = means.join(stds)
flat["diff"] = (flat["ai_mean"] - flat["human_mean"]).round(2)
flat["abs_diff"] = flat["diff"].abs()
flat = flat.round(2).sort_values("abs_diff", ascending=False)
flat.index.name = "features"
flat.to_csv(os.path.join(OUT_DIR, "summary_stats.csv"))
print("\nSaved: summary_stats.csv")

# FIG 1: Bar chart

fig, ax = plt.subplots(figsize=(6, 4))
counts = df["label"].value_counts().sort_index()
ax.bar(["Human (0)", "AI (1)"], counts.values, color=["#3b82f6", "#ef4444"])
ax.set_title("Bar chart")
ax.set_xlabel("Label")
ax.set_ylabel("Sentences")
for i, v in enumerate(counts.values):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "bar_chart.png"), bbox_inches="tight")
plt.close()
print("Saved: bar_chart.png")

# FIG 2: FEATURE HISTOGRAMS (AI vs Human)


core_feats = [
    "avg_word_len", "vocab_div_ratio", "complex_word_ratio",
    "stopword_ratio", "char_entropy", "rep_bigram",
    "ai_tell_count", "upper_letter_ratio",
]

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, feat in enumerate(core_feats):
    upper = df[feat].quantile(0.99)
    for lab, color, name in [(0, "#3b82f6", "Human"), (1, "#ef4444", "AI")]:
        data = df.loc[df["label"] == lab, feat]
        data = data[data <= upper]
        axes[i].hist(data, bins=40, alpha=0.55, color=color,
                     label=name, density=True)
    axes[i].set_title(feat, fontsize=10)
    axes[i].set_xlabel(feat, fontsize=8)
    axes[i].set_ylabel("Density", fontsize=8)
    axes[i].legend(fontsize=8)

fig.suptitle("Feature distributions by label (Human vs AI)", fontsize=14, y=1.00)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "feature_histograms.png"), bbox_inches="tight")
plt.close()
print("Saved: feature_histograms.png")

# FIG 3: CORRELATION HEATMAP

corr = df[FEATURES].corr().round(2)

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, square=True, cbar_kws={"shrink": 0.7},
            annot_kws={"size": 8})
ax.set_title("Correlation heatmap")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "correlation_heatmap.png"), bbox_inches="tight")
plt.close()
print("Saved: correlation_heatmap.png")

# FIG 4: BOX PLOTS (AI vs Human per feature)


sample = df.sample(n=min(30000, len(df)), random_state=42)

fig, axes = plt.subplots(2, 6, figsize=(20, 8))
axes = axes.flatten()

for i, feat in enumerate(FEATURES):
    upper = sample[feat].quantile(0.99)
    data_h = sample.loc[(sample["label"] == 0) & (sample[feat] <= upper), feat]
    data_a = sample.loc[(sample["label"] == 1) & (sample[feat] <= upper), feat]

    bp = axes[i].boxplot(
        [data_h, data_a],
        tick_labels=["Human", "AI"],
        patch_artist=True,
        widths=0.6,
        showfliers=False,
    )
    for patch, color in zip(bp["boxes"], ["#3b82f6", "#ef4444"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    axes[i].set_title(feat, fontsize=10)
    axes[i].set_ylabel(feat, fontsize=8)
    axes[i].tick_params(axis="x", labelsize=8)
    axes[i].margins(y=0.025)

fig.suptitle("Feature distributions by label (Human vs AI)", fontsize=14, y=1.00)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "feature_boxplots.png"), bbox_inches="tight")
plt.close()
print("Saved: feature_boxplots.png")

# PRINT REPORT 

print("\nEDA SUMMARY:")

print(f"\nTotal sentences: {len(df):,}")
print(f"\nLabel balance: human={counts.get(0,0):,} | AI={counts.get(1,0):,}")
print(f"\nHuman %: {100 * counts.get(0,0) / len(df):.1f}%")
print(f"AI %:    {100 * counts.get(1,0) / len(df):.1f}%")

print(f"\nSentence length (chars):")
print(f"  min:    {df['char_count'].min()}")
print(f"  median: {df['char_count'].median():.0f}")
print(f"  mean:   {df['char_count'].mean():.1f}")
print(f"  max:    {df['char_count'].max()}")



print(f"\nAll outputs saved to: {OUT_DIR}/")
