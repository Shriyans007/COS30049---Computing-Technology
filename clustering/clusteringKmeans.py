import numpy as np
import matplotlib.pyplot as plt
import sklearn
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


pd.set_option('display.max_columns', 120)
pd.set_option('display.width', 160)

DATASET = "data/processed/final_dataset.csv"
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
# print("shape:", ai_gen_essays.shape) 

# | Data Check |

# print(ai_gen_essays['upper_letter_ratio'].describe())
# print(ai_gen_essays['ai_tell_count'].describe())
# print(ai_gen_essays['rep_bigram'].describe())
# print(ai_gen_essays['char_entropy'].describe())
# print(ai_gen_essays['semicolon_dash_count'].describe())
# print(ai_gen_essays['avg_word_len'].describe()) 
# print((ai_gen_essays['rep_bigram'] > 0).mean())
# print((ai_gen_essays['semicolon_dash_count'] > 0).mean())

# | Initial Test to find K - Including char_count and word_count Features |

# FEATURES = ['char_count', 'word_count', 'avg_word_len', 'vocab_div_ratio', 
#             'complex_word_ratio', 'stopword_ratio', 'semicolon_dash_count', 
#             'upper_letter_ratio', 'char_entropy', 'rep_bigram']
# X = ai_gen_essays[FEATURES]

# raw = KMeans(3, n_init=10, random_state=42).fit_predict(X)
# X_scaled = StandardScaler().fit_transform(X)
# scaled = KMeans(3, n_init=10, random_state=42).fit_predict(X_scaled)



# print("without scaling", np.bincount(raw)) # [248667 206685  20717] - Highly imbalanced raw counts, likely char_count or word_count taking over
# print("with scaling ", np.bincount(scaled)) # [118767 176007 181295]

# inertias = []
# sils = []
# k_range = range(2, 11)

# for k in k_range:
#     print(k)
#     kmeans = KMeans(n_clusters=k, random_state=42)
#     labels = kmeans.fit_predict(X_scaled)
#     inertias.append(kmeans.inertia_)
#     sils.append(silhouette_score(X_scaled, labels, sample_size=20000, random_state=30))
    
    
# fig, ax1 = plt.subplots(figsize=(6, 4))

# # Primary y-axis: Inertia (Elbow Method)
# ax1.plot(k_range, inertias, 'bo-', label='Inertia (Elbow)')
# ax1.set_xlabel('Number of Clusters k')
# ax1.set_ylabel('Inertia', color='b')
# ax1.tick_params(axis='y', labelcolor='b')

# # Secondary y-axis: Silhouette Score
# ax2 = ax1.twinx()
# ax2.plot(k_range, sils, 'go-', label='Silhouette Score')
# ax2.set_ylabel('Silhouette Score', color='g')
# ax2.tick_params(axis='y', labelcolor='g')

# # Title and Saved Plot :D
# plt.title('Elbow Method vs. Silhouette Score')
# save("Elbow_vs_Silhouette_V1.png")

# | Final X - Removal of aforementioned 2 Features for Better Clustering |

FEATURES_V2 = ['avg_word_len', 'vocab_div_ratio', 'complex_word_ratio', 'stopword_ratio',
               'semicolon_dash_count', 'upper_letter_ratio', 'char_entropy', 'rep_bigram']
X_V2 = ai_gen_essays[FEATURES_V2]

X_V2_scaled = StandardScaler().fit_transform(X_V2)

# | Elbow Method vs Silhouette Score to find K |

# inertias_V2 = []
# sils_V2 = []
# k_range = range(2, 11)

# for k in k_range:
#     print(k)
#     kmeans = KMeans(n_clusters=k, random_state=42)
#     labels = kmeans.fit_predict(X_V2_scaled)
#     inertias_V2.append(kmeans.inertia_)
#     sils_V2.append(silhouette_score(X_V2_scaled, labels, sample_size=20000, random_state=42))
    
# | Plots for Elbow vs Silhouette Score |
    
# fig, ax1 = plt.subplots(figsize=(6, 4))

# # y-axis: Inertia - Elbow Method
# ax1.plot(k_range, inertias_V2, 'bo-', label='Inertia (Elbow)')
# ax1.set_xlabel('Number of Clusters k')
# ax1.set_ylabel('Inertia', color='b')
# ax1.tick_params(axis='y', labelcolor='b')

# # Secondary y-axis: Silhouette Score
# ax2 = ax1.twinx()
# ax2.plot(k_range, sils_V2, 'go-', label='Silhouette Score')
# ax2.set_ylabel('Silhouette Score', color='g')
# ax2.tick_params(axis='y', labelcolor='g')

# # Title and Saved Plot :D
# plt.title('Elbow Method vs. Silhouette Score')
# save("Elbow_vs_Silhouette_V2.png")

# | Test of k to check peak Silhouette score |

# model = KMeans(n_clusters=5, random_state=42)
# pred_labels = model.fit_predict(X_V2_scaled)
# sil_score = silhouette_score(X_V2_scaled, pred_labels, sample_size=20000, random_state=42)
# print("Silhouette Score:", sil_score) # Silhouette Score: 0.2347677488470225

# | Check validity of Clusters depending on K |
# for k in [2, 5, 6]:
#     test = KMeans(k, n_init=10, random_state=42).fit_predict(X_V2_scaled)
#     print(f"\n k={k}", np.bincount(test))    
#  k=2 [267412 208657]
#  k=5 [216066  41991 151827  40675  25510]
#  k=6 [ 40561 147707 214512   2315  40341  30633]

# | Cluster Plot & Cluster Descirptions |

labels = KMeans(5, n_init=10, random_state=42).fit_predict(X_V2_scaled)
ai_gen_essays['cluster'] = labels

overall, spread = X_V2.mean(), X_V2.std()
for c in sorted(ai_gen_essays.cluster.unique()):
    g = ai_gen_essays[ai_gen_essays.cluster == c]
    z = (g[FEATURES_V2].mean() - overall) / spread # in standard deviations
    print(f"\ncluster {c} n={len(g)}")
    print(" more:", z.nlargest(2).round(2).to_dict())
    print(" less:", z.nsmallest(2).round(2).to_dict())
    
P = PCA(n_components=2, random_state=42).fit_transform(X_V2_scaled)
scatter = plt.scatter(P[:, 0], P[:, 1], c=labels, s=8, cmap="viridis")
handles, cluster_labels = scatter.legend_elements()
plt.legend(handles=handles, labels=cluster_labels, title= "Cluster #")
plt.title('Clustering of AI Generated Class')
save("Cluster_Plot.png")


# | Sentence Examples From Each Cluster |

for c in sorted(ai_gen_essays.cluster.unique()):
    print(f"\n Cluster {c} Examples:")
    examples = ai_gen_essays[ai_gen_essays.cluster == c]['text'].sample(5, random_state=42)
    for e in examples:
        print("-", e)
        
