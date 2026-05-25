import uvicorn
import sys
from pathlib import Path

# Add project root directory to path so imports work correctly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("Launching Dipti's AI Representative Backend Server...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
