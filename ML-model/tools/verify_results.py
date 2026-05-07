import importlib.util, os, sys
HERE = os.path.dirname(__file__) or os.getcwd()
MAIN_PATH = os.path.abspath(os.path.join(HERE, '..', 'main.py'))
spec = importlib.util.spec_from_file_location('main', MAIN_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules['main'] = mod
spec.loader.exec_module(mod)

# load artifacts
try:
    mod.load_artifacts()
    print('Artifacts loaded')
except Exception as e:
    print('Startup error:', e)
    raise

req = mod.RecommendRequest(budget=2200, square_feet=650, bedrooms=1, bathrooms=1, amenities_count=4, pets_allowed_bin=0)
res = None
try:
    res = mod.recommend(req)
except Exception as e:
    print('Recommend threw:', e)
    raise

print('\nReturned results count:', len(res))
db = mod.app.state.recommender_db
print('\nVerifying each returned item against the recommender_db:')
for i, item in enumerate(res):
    rid = item.get('id')
    found = False
    row = None
    # try numeric index
    try:
        idx = int(rid)
        if idx in db.index:
            found = True
            row = db.loc[idx]
    except Exception:
        pass
    # try string index
    if not found:
        if rid in db.index:
            found = True
            row = db.loc[rid]
    print(f"{i+1}. id={rid} -> {'FOUND' if found else 'MISSING'}")
    if found:
        # print some fields from dataset
        title_col = next((c for c in ['title','Title','name','Name'] if c in db.columns), None)
        price_col = next((c for c in ['price','Price','rent','Rent'] if c in db.columns), None)
        city_col = next((c for c in ['city','City','cityname'] if c in db.columns), None)
        desc_col = next((c for c in ['description','Description','desc','summary','details'] if c in db.columns), None)
        print('   dataset title ->', row.get(title_col, ''))
        if desc_col:
            print('   dataset desc  ->', (row.get(desc_col, '') or '')[:120])
        if price_col:
            print('   dataset price ->', row.get(price_col))
        if city_col:
            print('   dataset city  ->', row.get(city_col))
    else:
        print('   No matching row in recommender_db for id', rid)

print('\nVerification complete.')
