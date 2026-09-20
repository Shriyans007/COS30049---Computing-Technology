import numpy as np
import matplotlib.pyplot as plt
import sklearn
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
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

ai_gen_essays = essays[essays['label'] == 1].copy()
ai_gen_essays = ai_gen_essays.drop(columns=['numeric_digit_ratio']) # Over 75% of sentences had 0 numeric usage so not meaningful for clustering
ai_gen_essays = ai_gen_essays.reset_index(drop=True) # reset indexs to be correct after splitting classes
# print("shape:", ai_gen_essays.shape) # (534481, 18)

# | Data Check |

# print(ai_gen_essays['upper_letter_ratio'].describe())
# print(ai_gen_essays['numeric_digit_ratio'].describe())
# print(ai_gen_essays['avg_word_len'].describe()) # Only one huge outlier with max 307 length word. Average was between 5-6 characters per word

# | Initial Test to find K - Including char_count and word_count Features |

# FEATURES = ['char_count', 'word_count', 'avg_word_len', 'vocab_div_ratio', 
#             'complex_word_ratio', 'stopword_ratio', 'semicolon_dash_count', 
#             'upper_letter_ratio', 'is_first_sent', 'is_last_sent']
# X = ai_gen_essays[FEATURES]

# raw = KMeans(3, n_init=10, random_state=42).fit_predict(X)
# X_scaled = StandardScaler().fit_transform(X)
# scaled = KMeans(3, n_init=10, random_state=42).fit_predict(X_scaled)



# print("without scaling", np.bincount(raw)) # [279503 228427  26551] - Highly imbalanced raw counts, likely char_count or word_count taking over
# print("with scaling ", np.bincount(scaled)) # [210111 129779 194591]

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

# # Title and layout
# plt.title('Elbow Method vs. Silhouette Score')
# fig.tight_layout()
# plt.show()

# | Final X - Removal of aforementioned 2 Features for Better Clustering |

FEATURES_V2 = ['avg_word_len', 'vocab_div_ratio', 'complex_word_ratio', 'stopword_ratio',
               'semicolon_dash_count', 'upper_letter_ratio', 'is_first_sent', 'is_last_sent']
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

# # Title and layout
# plt.title('Elbow Method vs. Silhouette Score')
# fig.tight_layout()
# plt.show()

# | Test of k to check peak Silhouette score |

# model = KMeans(n_clusters=5, random_state=42)
# pred_labels = model.fit_predict(X_V2_scaled)
# sil_score = silhouette_score(X_V2_scaled, pred_labels, sample_size=20000, random_state=42)
# print("Silhouette Score:", sil_score)

# | Cluster Plot & Cluster Descirptions |

labels = KMeans(5, n_init=10, random_state=42).fit_predict(X_V2_scaled)
ai_gen_essays['cluster'] = labels

overall, spread = X_V2.mean(), X_V2.std()
for c in sorted(ai_gen_essays.cluster.unique()):
    g = ai_gen_essays[ai_gen_essays.cluster == c]
    z = (g[FEATURES_V2].mean() - overall) / spread # in standard deviations
    # print(f"\ncluster {c} n={len(g)}")
    # print(" more:", z.nlargest(2).round(2).to_dict())
    # print(" less:", z.nsmallest(2).round(2).to_dict())
    
# P = PCA(n_components=2, random_state=42).fit_transform(X_V2_scaled)
# plt.scatter(P[:, 0], P[:, 1], c=labels, s=8, cmap="viridis")
# plt.title('Clustering of AI Generated Class')
# plt.show()

# | Figure out where the extreme outlier is coming from |

# outlier_positions = np.where(P[:, 0] > 100)
# print(outlier_positions) # [380526]
# print(ai_gen_essays.iloc[380526]['text'])
# print(ai_gen_essays.iloc[380526][FEATURES_V2])

# | Sentence Examples From Each Cluster |

for c in sorted(ai_gen_essays.cluster.unique()):
    print(f"\n Cluster {c} Examples:")
    examples = ai_gen_essays[ai_gen_essays.cluster == c]['text'].sample(5, random_state=42)
    for e in examples:
        print("-", e)