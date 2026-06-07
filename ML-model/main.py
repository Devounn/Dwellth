from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os


app = FastAPI(title="Dwellth Recommender API")

MODEL_FEATURE_COLS = [
    "square_feet",
    "bathrooms",
    "bedrooms",
    "amenities_count",
    "pets_allowed_bin",
    "latitude",
    "longitude",
]

# Allow CORS from frontend during development. Adjust origins for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    budget: Optional[float] = None
    square_feet: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    amenities_count: Optional[float] = None
    pets_allowed_bin: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


CLUSTER_MAP = {
    0: "Cozy Standard",
    1: "Spacious Suite",
    2: "Balanced Duo",
    3: "Minimalist Starter",
}


def _try_load(path: str):
    if os.path.exists(path):
        return joblib.load(path)
    return None


@app.on_event("startup")
def load_artifacts():
    base = os.path.dirname(__file__)

    # Prefer artifacts colocated in this folder (ML-model/)
    pipeline_candidates = [
        os.path.join(base, "preprocessing_pipeline.joblib"),
        os.path.join(base, "preprocessing_pipeline.pkl"),
        os.path.join(base, "../api_artifacts/preprocessing_pipeline.joblib"),
        os.path.join(base, "../api_artifacts/preprocessing_pipeline.pkl"),
    ]
    pipeline = None
    for p in pipeline_candidates:
        pipeline = _try_load(p)
        if pipeline is not None:
            break

    k_candidates = [
        os.path.join(base, "kmeans_model.joblib"),
        os.path.join(base, "kmeans_model.pkl"),
        os.path.join(base, "../api_artifacts/kmeans_model.joblib"),
    ]
    kmeans = None
    for p in k_candidates:
        kmeans = _try_load(p)
        if kmeans is not None:
            break

    # Dataframes
    db_candidates = [
        os.path.join(base, "recommender_db.pkl"),
        os.path.join(base, "../api_artifacts/recommender_db.pkl"),
        os.path.join(base, "../recommender_db.pkl"),
    ]
    recommender_db = None
    for p in db_candidates:
        if os.path.exists(p):
            recommender_db = pd.read_pickle(p)
            break

    scaled_candidates = [
        os.path.join(base, "scaled_features_db.pkl"),
        os.path.join(base, "../api_artifacts/scaled_features_db.pkl"),
    ]
    scaled_features_db = None
    for p in scaled_candidates:
        if os.path.exists(p):
            try:
                scaled_features_db = pd.read_pickle(p)
            except Exception:
                scaled_features_db = joblib.load(p)
            break

    if pipeline is None or kmeans is None or recommender_db is None or scaled_features_db is None:
        missing = [
            name
            for name, val in [
                ("preprocessing_pipeline", pipeline),
                ("kmeans_model", kmeans),
                ("recommender_db", recommender_db),
                ("scaled_features_db", scaled_features_db),
            ]
            if val is None
        ]
        raise RuntimeError(f"Missing artifacts: {missing}")

    app.state.pipeline = pipeline
    app.state.kmeans = kmeans
    app.state.recommender_db = recommender_db
    app.state.scaled_features_db = scaled_features_db

    # compute medians for input features
    feature_cols = MODEL_FEATURE_COLS
    medians = {}
    for c in feature_cols:
        if c in recommender_db.columns:
            medians[c] = float(recommender_db[c].median())
        else:
            # fallback: try common variants
            alt = None
            for cand in [c, c.title(), c.replace("_"," ")]:
                if cand in recommender_db.columns:
                    alt = cand
                    break
            if alt is not None:
                medians[c] = float(recommender_db[alt].median())
            else:
                medians[c] = 0.0

    app.state.medians = medians


def _get_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


@app.post("/recommend")
def recommend(req: RecommendRequest):
    # Fill missing with medians
    med = app.state.medians
    features = [
        req.square_feet if req.square_feet is not None else med["square_feet"],
        req.bathrooms if req.bathrooms is not None else med["bathrooms"],
        req.bedrooms if req.bedrooms is not None else med["bedrooms"],
        req.amenities_count if req.amenities_count is not None else med["amenities_count"],
        int(req.pets_allowed_bin) if req.pets_allowed_bin is not None else int(med["pets_allowed_bin"]),
        req.latitude if req.latitude is not None else med["latitude"],
        req.longitude if req.longitude is not None else med["longitude"],
    ]

    pipeline = app.state.pipeline
    kmeans = app.state.kmeans

    fallback_scaling = False
    scaled_user = None
    try:
        features_df = pd.DataFrame([features], columns=MODEL_FEATURE_COLS)
        scaled_user = pipeline.transform(features_df)
    except Exception as e:
        # If the saved preprocessing pipeline is incompatible with the current
        # sklearn version or expects engineered features, fall back to a simple
        # z-score scaling on the raw numeric columns.
        fallback_scaling = True
        fallback_error = e

    df: pd.DataFrame = app.state.recommender_db

    # If fallback scaling is active we cannot reliably predict the trained
    # cluster (different feature set). Skip cluster filtering and operate on
    # the full DB (budget filter still applied). Otherwise predict cluster.
    pred_cluster = None
    closest_two_clusters = None
    if not fallback_scaling:
        try:
            # Transform user to get distances to all centroids
            distances = kmeans.transform(scaled_user)[0]
            # Find the indices of the closest two clusters
            closest_two_clusters = [int(x) for x in distances.argsort()[:2]]
            pred_cluster = closest_two_clusters[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Clustering error: {e}")

    price_col = _get_col(df, ["price", "Price", "rent", "Rent"])
    if price_col is None:
        raise HTTPException(status_code=500, detail="Could not find price column in recommender_db")

    cluster_col = _get_col(df, ["Predicted_Cluster", "predicted_cluster", "pred_cluster"])
    if cluster_col is None:
        cluster_col = "Predicted_Cluster" if "Predicted_Cluster" in df.columns else None

    if cluster_col is None:
        raise HTTPException(status_code=500, detail="Could not find cluster column in recommender_db")

    if not fallback_scaling:
        filtered = df[df[cluster_col].isin(closest_two_clusters)]
    else:
        filtered = df

    # filter by budget
    budget_val = features[0]
    filtered = filtered[filtered[price_col] <= budget_val]

    if filtered.shape[0] == 0:
        return []

    # Prepare scaled features subset
    if not fallback_scaling:
        scaled_db = app.state.scaled_features_db
        # scaled_db may be DataFrame or ndarray
        if isinstance(scaled_db, pd.DataFrame):
            try:
                scaled_subset = scaled_db.loc[filtered.index]
            except Exception:
                # fallback: assume same order
                scaled_subset = scaled_db.iloc[filtered.index]
        else:
            # numpy array: assume same ordering as recommender_db
            positions = app.state.recommender_db.index.get_indexer(filtered.index)
            scaled_subset = scaled_db[positions]
    else:
        # Fallback scaling: compute z-score on the raw numeric features we know.
        # Use the columns we expect to exist in the recommender DB.
        num_cols = [c for c in MODEL_FEATURE_COLS if c in app.state.recommender_db.columns]
        if len(num_cols) == 0:
            raise HTTPException(status_code=500, detail=f"Scaling error: {fallback_error}")

        # build numeric matrix for filtered rows
        X = filtered[num_cols].copy()
        # fill missing with medians from app.state (fallback)
        for c in num_cols:
            if c in X.columns:
                X[c] = X[c].fillna(app.state.medians.get(c, X[c].median()))
        means = X.mean()
        stds = X.std()
        # replace zeros or NaNs in std with 1.0 to avoid division errors
        stds = stds.replace(0, 1.0).fillna(1.0)
        scaled_subset = ((X - means) / stds).to_numpy()

        # construct scaled_user from the original request values
        user_vals = []
        for c in num_cols:
            # map our feature names to the request values or medians
            val = None
            if c == 'square_feet':
                val = req.square_feet if req.square_feet is not None else med['square_feet']
            elif c == 'bathrooms':
                val = req.bathrooms if req.bathrooms is not None else med['bathrooms']
            elif c == 'bedrooms':
                val = req.bedrooms if req.bedrooms is not None else med['bedrooms']
            elif c == 'amenities_count':
                val = req.amenities_count if req.amenities_count is not None else med['amenities_count']
            elif c == 'pets_allowed_bin':
                val = int(req.pets_allowed_bin) if req.pets_allowed_bin is not None else int(med['pets_allowed_bin'])
            elif c == 'latitude':
                val = req.latitude if req.latitude is not None else med['latitude']
            elif c == 'longitude':
                val = req.longitude if req.longitude is not None else med['longitude']
            else:
                val = med.get(c, 0.0)
            user_vals.append(val)

        user_arr = np.array(user_vals, dtype=float)
        scaled_user = ((user_arr - means.to_numpy()) / stds.to_numpy()).reshape(1, -1)

    # compute cosine similarity
    sims = cosine_similarity(scaled_user, scaled_subset)[0]

    sims_series = pd.Series(sims, index=filtered.index)
    filtered = filtered.copy()
    filtered["_similarity"] = sims_series

    # high value deals
    hv_col = _get_col(filtered, ["Is_High_Value_Deal", "is_high_value_deal", "High_Value_Deal"])
    if hv_col is None:
        # assume False if not present
        filtered["Is_High_Value_Deal"] = False
        hv_col = "Is_High_Value_Deal"

    pool_a = filtered[filtered[hv_col] == True].nlargest(5, "_similarity")
    pool_b = filtered[filtered[hv_col] == False].nlargest(20, "_similarity")

    combined = pd.concat([pool_a, pool_b]).head(25)

    # map cluster numbers to strings for returned results
    if cluster_col in combined.columns:
        combined[cluster_col] = combined[cluster_col].map(CLUSTER_MAP).fillna(combined[cluster_col])

    # Identify common fields
    title_col = _get_col(combined, ["Title", "title", "name", "Name"]) or combined.columns[0]
    description_col = _get_col(combined, ["body", "Description", "description", "desc", "summary", "details"]) or None
    city_col = _get_col(combined, ["cityname", "City", "city"]) or None
    beds_col = _get_col(combined, ["beds", "Beds", "Bedrooms", "bedrooms"]) or None
    baths_col = _get_col(combined, ["baths", "Baths", "Bathrooms", "bathrooms"]) or None
    sqft_col = _get_col(combined, ["sq_ft", "sqft", "square_feet", "Square_Feet"]) or None
    fair_price_col = _get_col(combined, ["Predicted_Fair_Price", "predicted_fair_price", "fair_price", "estimated_price"]) or None
    lat_col = _get_col(combined, ["latitude", "lat", "Latitude", "Lat"]) or None
    lon_col = _get_col(combined, ["longitude", "lon", "Longitude", "Lon"]) or None

    results: List[Dict[str, Any]] = []
    for idx, row in combined.iterrows():
        estimated_price = float(row.get(fair_price_col, 0)) if fair_price_col is not None and pd.notna(row.get(fair_price_col)) else None
        item = {
            "id": str(idx),
            "title": row.get(title_col, ""),
            "description": row.get(description_col, "") if description_col is not None else "",
            "city": row.get(city_col, "") if city_col is not None else "",
            "price": float(row.get(price_col, 0.0)),
            "beds": int(row.get(beds_col, 0)) if beds_col is not None and pd.notna(row.get(beds_col)) else None,
            "baths": float(row.get(baths_col, 0)) if baths_col is not None and pd.notna(row.get(baths_col)) else None,
            "sq_ft": float(row.get(sqft_col, 0)) if sqft_col is not None and pd.notna(row.get(sqft_col)) else None,
            "predicted_fair_price": estimated_price,
            "estimated_price": estimated_price,
            "lifestyle_tag": row.get(cluster_col, CLUSTER_MAP.get(pred_cluster) if not fallback_scaling else None),
            "is_high_value_deal": bool(row.get(hv_col, False)),
            "latitude": float(row.get(lat_col)) if lat_col is not None and pd.notna(row.get(lat_col)) else None,
            "longitude": float(row.get(lon_col)) if lon_col is not None and pd.notna(row.get(lon_col)) else None,
            "similarity": float(row.get("_similarity", 0.0)),
        }
        results.append(item)

    return results
