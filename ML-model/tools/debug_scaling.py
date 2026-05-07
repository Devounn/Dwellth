import importlib.util, os, sys
HERE = os.path.dirname(__file__) or os.getcwd()
MAIN_PATH = os.path.abspath(os.path.join(HERE, '..', 'main.py'))
spec = importlib.util.spec_from_file_location('main', MAIN_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules['main'] = mod
spec.loader.exec_module(mod)
mod.load_artifacts()
print('medians:', mod.app.state.medians)
df = mod.app.state.recommender_db
print('recommender_db cols:', list(df.columns)[:20])
num_cols = [c for c in ['budget','square_feet','bedrooms','bathrooms','amenities_count','pets_allowed_bin'] if c in df.columns]
print('num_cols:', num_cols)
filtered = df.copy()
# simple filter to simulate budget
filtered = filtered[filtered[filtered.columns[0]].notna()].head(10)
X = filtered[num_cols].copy()
for c in num_cols:
    if c in X.columns:
        X[c] = X[c].fillna(mod.app.state.medians.get(c, X[c].median()))
print('X head:\n', X.head())
means = X.mean()
stds = X.std().replace(0,1.0).fillna(1.0)
print('means:', means.to_dict())
print('stds:', stds.to_dict())
user_vals = []
req = type('R', (), {'budget':2200,'square_feet':650,'bedrooms':1,'bathrooms':1,'amenities_count':4,'pets_allowed_bin':0})
for c in num_cols:
    val = None
    if c == 'budget':
        val = req.budget if req.budget is not None else mod.app.state.medians['budget']
    elif c == 'square_feet':
        val = req.square_feet if req.square_feet is not None else mod.app.state.medians['square_feet']
    elif c == 'bedrooms':
        val = req.bedrooms if req.bedrooms is not None else mod.app.state.medians['bedrooms']
    elif c == 'bathrooms':
        val = req.bathrooms if req.bathrooms is not None else mod.app.state.medians['bathrooms']
    elif c == 'amenities_count':
        val = req.amenities_count if req.amenities_count is not None else mod.app.state.medians['amenities_count']
    elif c == 'pets_allowed_bin':
        val = int(req.pets_allowed_bin) if req.pets_allowed_bin is not None else int(mod.app.state.medians['pets_allowed_bin'])
    else:
        val = mod.app.state.medians.get(c, 0.0)
    user_vals.append(val)
print('user_vals:', user_vals)
user_arr = __import__('numpy').array(user_vals, dtype=float)
scaled_user = ((user_arr - means.to_numpy()) / stds.to_numpy()).reshape(1, -1)
print('scaled_user:', scaled_user)
