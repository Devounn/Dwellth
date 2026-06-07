import importlib.util
import sys
import os

# Add the project root to sys.path to allow imports to find modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load main.py from the hyphenated "ML-model" directory dynamically
main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ML-model/main.py'))
spec = importlib.util.spec_from_file_location("main", main_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["main"] = mod
spec.loader.exec_module(mod)

# Export the FastAPI app instance for Vercel
app = mod.app
