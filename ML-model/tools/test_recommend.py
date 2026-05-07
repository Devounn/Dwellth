import importlib.util
import os
import sys

HERE = os.path.dirname(__file__) or os.getcwd()
MAIN_PATH = os.path.join(HERE, '..', 'main.py')
MAIN_PATH = os.path.abspath(MAIN_PATH)

spec = importlib.util.spec_from_file_location('main', MAIN_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules['main'] = mod
spec.loader.exec_module(mod)

# call startup loader
try:
    mod.load_artifacts()
    print('Artifacts loaded')
except Exception as e:
    print('Startup error:', e)
    import traceback
    traceback.print_exc()
    raise

req = mod.RecommendRequest(
    budget=2200,
    square_feet=650,
    bedrooms=1,
    bathrooms=1,
    amenities_count=4,
    pets_allowed_bin=0,
)

try:
    res = mod.recommend(req)
    print('Result count:', len(res))
    for r in res[:3]:
        print(r)
except Exception as e:
    print('Recommend error:')
    import traceback
    traceback.print_exc()
    raise
