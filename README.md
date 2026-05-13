# Dwellth

An intelligent apartment recommendation engine powered by machine learning. Dwellth analyzes your preferences and budget to find apartments that match your lifestyle, with an interactive map to explore properties and compare estimated vs. actual prices.

<img width="1351" height="805" alt="Screenshot 2026-05-07 103206" src="https://github.com/user-attachments/assets/904e679f-1b0a-4add-9e60-f32216e46d4c" />
<img width="1895" height="829" alt="image" src="https://github.com/user-attachments/assets/2e35176d-d370-4393-9bc2-006c36137de6" />

## Features

- **Smart Recommendations**: ML-powered K-means clustering with 7-feature analysis (square footage, bathrooms, bedrooms, amenities, pet policy, and location coordinates)
- **Price Intelligence**: Compares actual listing prices with ML-predicted fair market prices
- **Interactive Map**: Leaflet-based map view with clickable markers and smooth navigation
- **High-Value Deal Detection**: Automatic identification of underpriced apartments
- **Lifestyle Tags**: Dynamic clustering that groups apartments by type (Cozy Standard, Spacious Suite, Balanced Duo, Minimalist Starter)
- **Similarity Scoring**: Ranked results showing how closely each apartment matches your search

## Tech Stack

**Backend:**
- FastAPI (async web framework)
- scikit-learn (ML clustering and similarity)
- pandas, numpy (data processing)
- joblib (model serialization)

**Frontend:**
- Vue 3 (UI framework)
- Vite (build tooling)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Leaflet (mapping)

**ML Pipeline:**
- K-means clustering (4 clusters)
- StandardScaler + SimpleImputer preprocessing
- Cosine similarity ranking

## Project Structure

```
Dwellth/
├── frontend/                    # Vue 3 web application
│   ├── src/
│   │   ├── App.vue             # Main shell component
│   │   ├── main.ts             # Vue app entry
│   │   ├── api.ts              # API client with caching
│   │   ├── styles.css          # Global theme and animations
│   │   └── components/
│   │       ├── HeroSearch.vue        # Search form
│   │       ├── ResultsSplitView.vue  # Card list + map layout
│   │       ├── ApartmentCard.vue     # Individual result card
│   │       ├── MapView.vue           # Leaflet map + details footer
│   │       └── IntroSpinner.vue      # Loading overlay
│   ├── package.json
│   └── .env.example             # API endpoint config template
│
├── ML-model/                    # FastAPI backend
│   ├── main.py                  # API server with /recommend endpoint
│   ├── requirements.txt         # Python dependencies
│   └── tools/                   # Debugging utilities
│       ├── test_recommend.py    # Local endpoint testing
│       ├── verify_results.py    # Dataset validation
│       └── debug_scaling.py     # Scaling diagnostics
│
├── Model_Final_Project.ipynb    # ML training notebook
├── kmeans_model.joblib          # Trained K-means model
├── preprocessing_pipeline.joblib  # Preprocessing pipeline
├── recommender_db.pkl           # Full apartment dataset
├── scaled_features_db.pkl       # Pre-scaled feature matrix
└── .gitignore                   # Git exclusions
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip (Python package manager)
- npm (Node package manager)

### Backend Setup

1. **Clone and navigate:**
   ```bash
   cd c:\projects\Dwellth
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ML-model/requirements.txt
   ```
   *Note: scikit-learn is pinned to 1.6.1 for compatibility with serialized models*

### Frontend Setup

3. **Install Node dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Environment Configuration

4. **Copy frontend environment template:**
   ```bash
   copy frontend\.env.example frontend\.env
   ```
   Edit `frontend/.env` if your backend runs on a different address (default: `http://localhost:8000`)

5. **Run the Jupyter Notebook:**
   Run the Model-Final-Project.ipynb to get the necessary .pkl and .joblib files
   
## Running Locally

### Start Backend (Terminal 1)

```bash
python -m uvicorn ML-model.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs` (Swagger UI)

### Start Frontend Dev Server (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Build for Production

**Frontend:**
```bash
cd frontend
npm run build
# Output: dist/ folder (ready for deployment)
```

**Backend:**
```bash
# Run with production settings
python -m uvicorn ML-model.main:app --host 0.0.0.0 --port 8000
```

## How It Works

### Recommendation Engine

1. **User Input**: Search form collects budget, square footage, bedrooms, bathrooms, amenities count, and pet policy
2. **Preprocessing**: Missing values filled with dataset medians; features scaled using StandardScaler
3. **Clustering**: K-means predicts apartment cluster (0-3) based on scaled features
4. **Filtering**: Database filtered to matching cluster + budget range
5. **Ranking**: Cosine similarity computed between user vector and each candidate
6. **Pooling**: Top results split into:
   - **Pool A** (5 high-value deals): Apartments below estimated fair price
   - **Pool B** (20 standard): Remaining ranked by similarity
7. **Response**: Top 25 apartments with details, estimated price, and lifestyle tag

### API Endpoint

**POST /recommend**

Request:
```json
{
  "budget": 2200,
  "square_feet": 650,
  "bedrooms": 1,
  "bathrooms": 1,
  "amenities_count": 4,
  "pets_allowed_bin": 0
}
```

Response (array of apartments):
```json
[
  {
    "id": "apt_001",
    "title": "Cozy Downtown Studio",
    "description": "Beautiful apartment in vibrant neighborhood...",
    "city": "San Francisco",
    "price": 2100,
    "estimated_price": 2250,
    "beds": 1,
    "baths": 1,
    "sq_ft": 650,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "lifestyle_tag": "Cozy Standard",
    "is_high_value_deal": true,
    "similarity": 0.87
  }
]
```

## Frontend Features

### Search Form
Intuitive input for all recommendation parameters with custom styling and range sliders.

### Results View
- **Card List**: Shows apartment title, address, price, beds/baths/sqft, similarity percentage, and high-value badge
- **Interactive Map**: Leaflet map with markers; click any card to recenter and open details popup
- **Scrollable Footer**: Shows selected apartment with price comparison (actual vs. estimated) and description

### Animations
- Staggered fade-in reveal animations on scroll
- Smooth header collapse on scroll
- Map recenter transitions
- Gradient UI effects

## Troubleshooting

### Backend Won't Start
- **Error: "ModuleNotFoundError: No module named 'sklearn'"**
  - Reinstall: `pip install -r ML-model/requirements.txt`
- **Error: "scikit-learn version mismatch"**
  - Ensure scikit-learn is exactly 1.6.1: `pip install scikit-learn==1.6.1`
- **Error: "No such file: kmeans_model.joblib"**
  - Artifacts must be in `ML-model/` or `api_artifacts/` directories

### Frontend Won't Connect to Backend
- Verify backend is running on correct port (default 8000)
- Check CORS: Backend should show "Uvicorn running on" message
- Verify `VITE_API_BASE` in `frontend/.env` matches backend address
- Clear browser cache (or hard refresh with Ctrl+Shift+R)

### Estimates Show as Dashes
- Backend cache may be stale; clear it by restarting the application
- Ensure `predicted_fair_price` field exists in dataset

## Development Notes

### Python Environment
- Tested with Python 3.10-3.14
- All packages pinned to compatible versions in `requirements.txt`

### Frontend Development
- Uses Vite HMR (Hot Module Replacement) for instant feedback
- TypeScript strict mode enabled
- Tailwind CSS JIT compiled

### Data Model (7 Features)
Clustering trained on: `square_feet`, `bathrooms`, `bedrooms`, `amenities_count`, `pets_allowed_bin`, `latitude`, `longitude`

### Cluster Mapping
- **0**: Cozy Standard
- **1**: Spacious Suite
- **2**: Balanced Duo
- **3**: Minimalist Starter

## Performance Notes

- Frontend production build: ~240KB JS, 52KB CSS
- First recommendation request: ~200-500ms (scaling, prediction, similarity compute)
- Subsequent searches: <100ms (in-memory caching, 60s TTL)
- Map renders 14-20 markers depending on dataset lat/lon coverage

## License

See [LICENSE](LICENSE) file for details.

---

**Built with ❤️ as a Machine Learning Lecture Final Project**
Final Score : 
