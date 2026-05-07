# Project Context: "Dwellth" - AI-Powered Apartment Recommender
Act as an Expert Full-Stack Developer and Machine Learning Engineer. I am building a web application called "Dwellth". 
The Vue.js frontend is already initialized, and the machine learning models have been trained and exported. 
I need you to write the backend API (FastAPI) and the core frontend components (Vue 3) to stitch this together.

## Tech Stack
* Backend: Python, FastAPI, Pandas, Scikit-Learn, Joblib
* Frontend: Vue 3 (Composition API), Tailwind CSS (for modern UI), Leaflet.js (for map integration)

## Current Project State
I have an `api_artifacts` folder containing the following ML exports:
1. `preprocessing_pipeline.joblib` (StandardScaler & Imputer)
2. `kmeans_model.joblib` (Lifestyle clustering model)
3. `stacking_regressor.joblib` (Price prediction ensemble model)
4. `recommender_db.pkl` (Pandas DataFrame with apartment details, lat/long, price, and pre-calculated 'Predicted_Cluster' and 'Is_High_Value_Deal')
5. `scaled_features_db.pkl` (Pandas DataFrame with scaled features for cosine similarity calculation)

## Task 1: The FastAPI Backend (`main.py`)
Write a FastAPI application that loads these artifacts on startup and exposes a `/recommend` POST endpoint. 
The endpoint should accept user preferences: `budget`, `square_feet`, `bedrooms`, `bathrooms`, `amenities_count`, and `pets_allowed_bin`.

**The Business Logic for `/recommend`:**
1. Process User Input: If a feature is missing from the user request, fill it with the training data median. Scale the input using the `preprocessing_pipeline`.
2. Predict Lifestyle: Pass the scaled input to the `kmeans_model` to get the user's predicted cluster (0, 1, 2, or 3).
3. Filter the Database: Filter `recommender_db` to only include apartments in the predicted cluster that are <= the user's `budget`.
4. Calculate Similarity: Calculate the Cosine Similarity between the user's scaled input and the `scaled_features_db` for the filtered apartments.
5. **The Sorting Requirement:** - Pool A: Get the Top 5 apartments where `Is_High_Value_Deal == True`, sorted by highest Cosine Similarity.
   - Pool B: Get the Top 20 apartments where `Is_High_Value_Deal == False`, sorted by highest Cosine Similarity.
   - Combine Pool A and Pool B (yielding up to 25 results total).
6. Data Mapping: Map the raw cluster numbers to strings before returning JSON:
   - 0 -> "Cozy Standard"
   - 1 -> "Spacious Suite"
   - 2 -> "Balanced Duo"
   - 3 -> "Minimalist Starter"
7. Return the final JSON array including latitude and longitude.

## Task 2: The Vue 3 Frontend
Write the Vue components to consume this API and display the results with a highly polished, modern UI using Tailwind CSS.

**Required Components:**
1. **Hero/Search Section:** A clean form to input budget, sq ft, bedrooms, bathrooms, amenities, and pets (checkbox).
2. **Results Layout (Split View):** - Left side: A scrollable list of Apartment Cards.
   - Right side: An interactive Map (using Leaflet.js / vue-leaflet) showing markers for all recommended apartments.
3. **Apartment Cards:** - Must clearly display the Title, City, Price, Beds, Baths, and Sq Ft.
   - Include a styled Badge for the "Lifestyle Tag" (e.g., "Spacious Suite").
   - Include a highlighted/glowing Badge saying "🔥 High Value Deal" if `Is_High_Value_Deal` is true.

Please provide the code for the FastAPI `main.py`, the main Vue view/component, and the integration of the Leaflet map. Let's start with the FastAPI backend structure.