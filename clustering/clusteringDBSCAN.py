import numpy as np
import matplotlib.pyplot as plt
import sklearn
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA

pd.set_option('display.max_columns', 120)
pd.set_option('display.width', 160)

DATASET = "C:/Users/lollo/Documents/School/Comp tech/Assignment2/clean_dataset.csv"
essays = pd.read_csv(DATASET)

# print(essays.head(10))

# print(essays.columns.tolist())

# print("dtypes ", set(essays.dtypes.astype(str))) # still has string
# print("missing ", essays.isnull().sum().sum()) # 0
# print("duplicates ", essays.duplicated().sum()) # 0

CHARTS = "charts"
os.makedirs(CHARTS, exist_ok=True)

def save(name, dpi=140):
    path = os.path.join(CHARTS, name)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print("saved chart:", path)
        
    

ai_gen_essays = essays[essays['label'] == 1].copy()
ai_gen_essays = ai_gen_essays.drop(columns=['numeric_digit_ratio']) # Over 75% of sentences had 0 numeric usage so not meaningful for clustering
ai_gen_essays = ai_gen_essays.reset_index(drop=True) # reset indexs to be correct after splitting classes
ai_gen_essays = ai_gen_essays.drop(index=[380526, 441145, 484810, 509270, 512775, 514742])    # drop extreme outlier row
ai_gen_essays = ai_gen_essays.reset_index(drop=True)
# print("shape:", ai_gen_essays.shape) # (534481, 18)


FEATURES_V2 = ['avg_word_len', 'vocab_div_ratio', 'complex_word_ratio', 'stopword_ratio',
               'semicolon_dash_count', 'upper_letter_ratio', 'is_first_sent', 'is_last_sent']
X_V2 = ai_gen_essays[FEATURES_V2]

X_V2_scaled = StandardScaler().fit_transform(X_V2)

# nearneigh = NearestNeighbors(n_neighbors=16).fit(X_V2_scaled) # neighbours = 16 as 8 Features x 2 
# distance, _ = nearneigh.kneighbors(X_V2_scaled)

# plt.plot(np.sort(distance[:, -1]))
# # plt.axhline(0.3, color="pink", ls="--")
# plt.xlabel("points, sorted by distance to their 16th neighbour")
# plt.ylabel("distance")
# save("init_k_distance.png")

# | Check Outliers & Their Validity | 
# print(np.sort(distance[:, -1])[-30:])
# outlier_pos = np.where(distance[:, -1] > 20)
# print(outlier_pos)
# # All printed strange strings of random alphanumeric strings and ending with "Please explain like im five."
# print("1:", ai_gen_essays.iloc[441145]['text'])
# print("\n 2:", ai_gen_essays.iloc[484810]['text'])
# print("\n 3:",ai_gen_essays.iloc[509270]['text'])
# print("\n 4:",ai_gen_essays.iloc[512775]['text'])
# print("\n 5:",ai_gen_essays.iloc[514742]['text'])

# | DBSCAN Clustering :D | 

db = DBSCAN(eps=1, min_samples=16).fit_predict(X_V2_scaled)
n_clusters = len(set(db)) - (1 if -1 in db else 0)
noise = list(db).count(-1)

print(f"Found {n_clusters} clusters.")
print(f"Noise is: {noise} ({noise/len(db):.0%})")

ai_gen_essays['dbscan_cluster'] = db

overall, spread = X_V2.mean(), X_V2.std()
for c in sorted(ai_gen_essays.dbscan_cluster.unique()):
    g = ai_gen_essays[ai_gen_essays.dbscan_cluster == c]
    z = (g[FEATURES_V2].mean() - overall) / spread # in standard deviations
    label = "NOISE" if c == -1 else f"cluster {c}" # decide whether actual cluster or noise
    print(f"\n{label} n={len(g)}")
    print(" more:", z.nlargest(2).round(2).to_dict())
    print(" less:", z.nsmallest(2).round(2).to_dict())
    

P = PCA(n_components=2, random_state=42).fit_transform(X_V2_scaled)
plt.scatter(P[:, 0], P[:, 1], c=db, s=8, cmap="viridis")
plt.title('DBSCAN Clustering of AI Generated Class')
save("DBSCAN_Cluster_Plot.png")


# | Sentence Examples From Each Cluster |

for c in sorted(ai_gen_essays.dbscan_cluster.unique()):
    label = "NOISE" if c == -1 else f"cluster {c}" # decide whether actual cluster or noise
    print(f"\n {label} Examples:")
    examples = ai_gen_essays[ai_gen_essays.dbscan_cluster == c]['text'].sample(5, random_state=42)
    for e in examples:
        print("-", e)