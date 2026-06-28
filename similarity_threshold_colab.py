# =====================================================================
# SIMILARITY THRESHOLD TRADE-OFF SIMULATOR (GOOGLE COLAB VERSION)
# =====================================================================
# Paste this entire block into a single code cell in your Colab notebook.
# NOTE: Make sure you upload the following files from your local 'ML-model' 
# directory to your Colab environment:
#   1. preprocessing_pipeline.joblib
#   2. kmeans_model.joblib
#   3. recommender_db.pkl
#   4. scaled_features_db.pkl
#
# If you place them in the default Colab directory (/content/), set 
# ARTIFACTS_PATH = "/content/" below.
# =====================================================================

import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

# Set this to the folder containing your uploaded model files
# (For local testing: r"C:\projects\Dwell\ML-model" or equivalent path)
ARTIFACTS_PATH = "./ML-model" 

# File paths
pipeline_path = os.path.join(ARTIFACTS_PATH, "preprocessing_pipeline.joblib")
kmeans_path = os.path.join(ARTIFACTS_PATH, "kmeans_model.joblib")
db_path = os.path.join(ARTIFACTS_PATH, "recommender_db.pkl")
scaled_db_path = os.path.join(ARTIFACTS_PATH, "scaled_features_db.pkl")

# Check if files exist to avoid path crashes in Colab
missing_files = [f for f in [pipeline_path, kmeans_path, db_path, scaled_db_path] if not os.path.exists(f)]
if missing_files:
    print("Warning: The following files were not found at the specified path:")
    for mf in missing_files:
        print(f"  - {mf}")
    print("\nPlease upload these files to your Google Colab folder or correct the ARTIFACTS_PATH.")
    print("Using temporary mock data to show you how the graph will look...")
    
    # Generate mock data for demo demonstration if files are not yet uploaded
    np.random.seed(42)
    thresholds = np.linspace(0.0, 1.0, 21)
    coverage = 100 / (1 + np.exp(10 * (thresholds - 0.82))) # Sigmoid shape
    avg_volume = 120 * np.exp(-4 * thresholds) # Exponential decay shape
else:
    # 1. Load trained models and database artifacts
    print("Loading serialized artifacts...")
    pipeline = joblib.load(pipeline_path)
    kmeans = joblib.load(kmeans_path)
    recommender_db = pd.read_pickle(db_path)
    
    try:
        scaled_features_db = pd.read_pickle(scaled_db_path)
    except Exception:
        scaled_features_db = joblib.load(scaled_db_path)
        
    if isinstance(scaled_features_db, np.ndarray):
        scaled_features_df = pd.DataFrame(scaled_features_db, index=recommender_db.index)
    else:
        scaled_features_df = scaled_features_db

    kmeans_features = [
        'square_feet', 'bathrooms', 'bedrooms',
        'amenities_count', 'pets_allowed_bin',
        'latitude', 'longitude'
    ]

    # 2. Simulate 200 diverse search queries
    print("Running query simulation (n=200 requests)...")
    np.random.seed(42)
    num_simulations = 200

    simulated_queries = []
    for _ in range(num_simulations):
        query = {
            'square_feet': np.random.uniform(300, 2000),
            'bathrooms': float(np.random.choice([1, 1.5, 2, 2.5, 3])),
            'bedrooms': float(np.random.choice([1, 2, 3, 4])),
            'amenities_count': float(np.random.randint(0, 10)),
            'pets_allowed_bin': float(np.random.choice([0, 1])),
            'latitude': np.random.uniform(recommender_db['latitude'].min(), recommender_db['latitude'].max()),
            'longitude': np.random.uniform(recommender_db['longitude'].min(), recommender_db['longitude'].max()),
            'budget': np.random.uniform(600, 3500)
        }
        simulated_queries.append(query)

    # 3. Test thresholds from 0.0 to 1.0
    thresholds = np.linspace(0.0, 1.0, 21)
    coverage = []    # % of users getting at least 1 recommendation
    avg_volume = []  # Average number of recommendations returned

    for threshold in thresholds:
        success_count = 0
        volumes = []
        
        for q in simulated_queries:
            # Create user preference DataFrame
            user_df = pd.DataFrame([q])[kmeans_features]
            user_scaled = pipeline.transform(user_df)
            
            # Match cluster
            user_cluster = kmeans.predict(user_scaled)[0]
            
            # Filter DB (Budget + Cluster)
            valid_indices = recommender_db[
                (recommender_db['Predicted_Cluster'] == user_cluster) &
                (recommender_db['price'] <= q['budget'])
            ].index
            
            if len(valid_indices) == 0:
                volumes.append(0)
                continue
                
            candidate_features = scaled_features_df.loc[valid_indices]
            
            # Calculate cosine similarities
            sims = cosine_similarity(user_scaled, candidate_features)[0]
            
            # Apply similarity threshold
            filtered_sims = sims[sims >= threshold]
            
            count = len(filtered_sims)
            volumes.append(count)
            if count > 0:
                success_count += 1
                
        coverage.append((success_count / num_simulations) * 100)
        avg_volume.append(np.mean(volumes))

# 4. Generate the Visualization
print("Generating graph...")
fig, ax1 = plt.subplots(figsize=(11, 6.5))

# Plot Coverage Line (Left Y-Axis)
color = '#1E3A8A'  # Navy Blue
ax1.set_xlabel('Similarity Threshold (Cosine Score Cutoff)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_ylabel('Query Coverage (% of queries returning ≥ 1 match)', color=color, fontsize=12, fontweight='bold')
line1 = ax1.plot(thresholds, coverage, color=color, marker='o', linewidth=2.5, label='Query Coverage (%)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle=':', alpha=0.6)

# Plot Volume Line (Right Y-Axis)
ax2 = ax1.twinx()  
color = '#EA580C'  # Orange Accent
ax2.set_ylabel('Average Recommendation Count (Curation Density)', color=color, fontsize=12, fontweight='bold')
line2 = ax2.plot(thresholds, avg_volume, color=color, marker='s', linewidth=2.5, linestyle='--', label='Avg Recommendation Vol.')
ax2.tick_params(axis='y', labelcolor=color)

# Highlight the "Optimal Curation Balance" region (0.70 - 0.80)
ax1.axvspan(0.70, 0.80, color='#10B981', alpha=0.18, label='Optimal Threshold Zone (0.70 - 0.80)')

# Graph Details & Legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines + [plt.Rectangle((0,0),1,1,fc='#10B981',alpha=0.18)], 
           labels + ['Optimal Threshold Zone (0.70 - 0.80)'], 
           loc='upper right', frameon=True, facecolor='white', edgecolor='lightgray')

# Add explanatory callout texts on the graph
ax1.annotate('High Curation (Empty Results Risk)\nSimilarity too strict', 
             xy=(0.9, 10), xytext=(0.6, 25),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
             fontsize=9.5, color='gray', bbox=dict(boxstyle="round,pad=0.3", fc="#FEF2F2", ec="#FCA5A5", lw=1))

ax1.annotate('Low Curation (Cognitive Overload)\nSimilarity too loose', 
             xy=(0.2, 95), xytext=(0.3, 75),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
             fontsize=9.5, color='gray', bbox=dict(boxstyle="round,pad=0.3", fc="#EFF6FF", ec="#BFDBFE", lw=1))

plt.title('Similarity Threshold Trade-Off Analysis\nQuery Coverage vs. Recommendation Curation Density', 
          fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.show()
