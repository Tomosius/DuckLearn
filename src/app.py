from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import routes_config_duckdb  # ✅ absolute import (always works)

app = FastAPI(title="DuckLearn", version="1.0")

app.include_router(routes_config_duckdb.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("⚙️ Running in DEVELOPMENT mode (no static files mounted).")