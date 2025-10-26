"""
DuckLearn — Unified FastAPI Application
---------------------------------------

This FastAPI app supports both DEVELOPMENT and PRODUCTION modes.

✅ DEVELOPMENT MODE (currently active):
   - Backend runs on Uvicorn
   - Frontend (SvelteKit) runs separately via Vite (`npm run dev`)
   - FastAPI exposes API routes only (no static files)
   - CORS is enabled for http://localhost:5173 so Vite can talk to the API

✅ PRODUCTION MODE (commented below):
   - After `npm run build`, FastAPI serves both:
       • Compiled static assets from `frontend/build/assets`
       • The main `index.html` at "/"
   - No CORS middleware needed, since frontend and backend share origin
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="DuckLearn", version="1.0")

# ----------------------------------------------------------
# 🧠 Common API routes (active in all modes)
# ----------------------------------------------------------
@app.get("/api/hello")
def read_root():
    return {"message": "Hello from Tomosius FastAPI!"}


# ----------------------------------------------------------
# 💻 DEVELOPMENT MODE (currently active)
# ----------------------------------------------------------
# ✅ Allow Vite (SvelteKit) dev server to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ In DEV mode, we do NOT serve static files.
#    The frontend runs live on port 5173 (via Vite).
#
# Example:
#   npm run dev   → frontend
#   uv run uvicorn src.ducklearn.app:app --reload   → backend
#
print("⚙️  Running in DEVELOPMENT mode (no static files mounted).")


# ----------------------------------------------------------
# 🚀 PRODUCTION MODE (commented for now)
# ----------------------------------------------------------
"""
# ✅ When ready for production, uncomment below:

# Define paths to built Svelte frontend
STATIC_DIR = "frontend/build"
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")

# Serve compiled static assets (JS, CSS, images)
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="static")

# Serve the main index.html file
@app.get("/", response_class=FileResponse)
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

print(f"🚀 Running in PRODUCTION mode (serving static files from {STATIC_DIR}).")
"""