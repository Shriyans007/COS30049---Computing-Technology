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

DATASET = "data/processed/final_dataset.csv"
essays = pd.read_csv(DATASET)

# print(essays.head(10))

# print(essays.columns.tolist())

# print("missing: ", essays.isnull().sum().sum()) # 0
# print("duplicates: ", essays.duplicated().sum()) # 0

CHARTS = "charts"
os.makedirs(CHARTS, exist_ok=True)

def save(name, dpi=140):
    path = os.path.join(CHARTS, name)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print("saved chart:", path)
        
    

ai_gen_essays = essays[essays['label'] == 1].copy()

# | Final X |

FEATURES_V2 = ['avg_word_len', 'vocab_div_ratio', 'complex_word_ratio', 'stopword_ratio',
               'semicolon_dash_count', 'upper_letter_ratio', 'char_entropy', 'rep_bigram']
X_V2 = ai_gen_essays[FEATURES_V2]

X_V2_scaled = StandardScaler().fit_transform(X_V2)

# nearneigh = NearestNeighbors(n_neighbors=16).fit(X_V2_scaled) # neighbours = 16 as 8 Features x 2 
# distance, _ = nearneigh.kneighbors(X_V2_scaled)

# plt.plot(np.sort(distance[:, -1]))
# plt.ylim(0, 4)
# plt.axhline(1, color="pink", ls="--")
# plt.xlabel("points, sorted by distance to their 16th neighbour")
# plt.ylabel("distance")
# save("init_k_distance.png")

# | Test For Best Epsilon Number | 

# X_test_sample = X_V2_scaled[np.random.RandomState(42).choice(len(X_V2_scaled), 150000, replace=False)]

# for eps in [0.5, 0.8, 1, 1.3]:
#     print(f"eps={eps}: ")
#     test = DBSCAN(eps=eps, min_samples=16).fit_predict(X_test_sample)
#     n_clusters = len(set(test)) - (1 if -1 in test else 0)
#     noise = list(test).count(-1)
#     print(f"Found {n_clusters} clusters.")
#     print(f"Noise is: {noise} ({noise/len(test):.1%})")
    
# | Results | 
# eps=0.5: 
# Found 43 clusters.
# Noise is: 28379 (18.9%)
# eps=0.8: 
# Found 28 clusters.
# Noise is: 7576 (5.1%)
# eps=1: 
# Found 22 clusters.
# Noise is: 3771 (2.5%)
# eps=1.3: 
# Found 18 clusters.
# Noise is: 1473 (1.0%) 



# | DBSCAN Clustering :D | 

sample = np.random.RandomState(42).choice(len(X_V2_scaled), 150000, replace=False)
X_Sample =  X_V2_scaled[sample]

sample_set = ai_gen_essays.iloc[sample].copy().reset_index(drop=True)

print(X_Sample.shape, len(sample_set))

db = DBSCAN(eps=1, min_samples=16).fit_predict(X_Sample)
n_clusters = len(set(db)) - (1 if -1 in db else 0)
noise = list(db).count(-1)

print(f"Found {n_clusters} clusters.")
print(f"Noise is: {noise} ({noise/len(db):.1%})")

sample_set['dbscan_cluster'] = db

overall, spread = X_V2.mean(), X_V2.std()
for c in sorted(sample_set.dbscan_cluster.unique()):
    g = sample_set[sample_set.dbscan_cluster == c]
    z = (g[FEATURES_V2].mean() - overall) / spread # in standard deviations
    label = "NOISE" if c == -1 else f"cluster {c}" # decide whether actual cluster or noise
    print(f"\n{label} n={len(g)}")
    print(" more:", z.nlargest(2).round(2).to_dict())
    print(" less:", z.nsmallest(2).round(2).to_dict())
    

P = PCA(n_components=2, random_state=42).fit_transform(X_Sample)
scatter = plt.scatter(P[:, 0], P[:, 1], c=db, s=8, cmap="viridis")
# handles, cluster_labels = scatter.legend_elements()
# plt.legend(handles=handles, labels=cluster_labels, title= "Cluster #")
plt.title('DBSCAN Clustering of AI Generated Class')
save("DBSCAN_Cluster_Plot.png")


# | Sentence Examples From Each Cluster |

# for c in sorted(sample_set.dbscan_cluster.unique()):
#     g = sample_set[sample_set.dbscan_cluster == c]
#     label = "NOISE" if c == -1 else f"cluster {c}" # decide whether actual cluster or noise
#     print(f"\n {label} Examples:")
#     examples = sample_set[sample_set.dbscan_cluster == c]['text'].sample(min(5, len(g)), random_state=42)
#     for e in examples:
#         print("-", e)

# | Silhouette Score For DBSCAN |

# no_noise = db != -1
# sil_score = silhouette_score(X_Sample[no_noise], db[no_noise], sample_size=20000, random_state=42)
# print(f"Silhouette Score (No Noise): {sil_score:.3f}") # Silhouette Score (No Noise): 0.201

# sil_score = silhouette_score(X_Sample, db, sample_size=20000, random_state=42)
# print(f"Silhouette Score (Noise): {sil_score:.3f}") # Silhouette Score (Noise): 0.188
