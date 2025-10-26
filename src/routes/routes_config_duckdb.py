from fastapi import APIRouter, Body
from config.config_duckdb import DuckDBConfig

router = APIRouter(prefix="/api/config", tags=["DuckDB Config"])

# --- Initialize config instance ---
duckdb_config = DuckDBConfig()


@router.get("")
def get_duckdb_config():
    """Return current DuckDB configuration."""
    return duckdb_config.to_dict()


@router.put("")
def update_duckdb_config(new_config: dict = Body(...)):
    """
    Update DuckDB configuration dynamically.
    Example JSON payload:
    {
        "memory_limit": "8GB",
        "threads": 8,
        "enable_progress_bar": false
    }
    """
    for key, value in new_config.items():
        if hasattr(duckdb_config, key):
            setattr(duckdb_config, key, value)

    return duckdb_config.to_dict()