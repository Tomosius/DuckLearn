from pathlib import Path
from typing import Literal
import os
import psutil

class DuckDBConfig:
    """Holds configuration settings specific to DuckDB."""

    def __init__(
        self,
        db_type: Literal["memory", "persistent"] = "memory",
        db_path: str | None = None,
        memory_limit: str | None = None,  # auto-detect if None
        threads: int | None = None,       # auto-detect if None
        enable_progress_bar: bool = True,
        read_only: bool = False,
        default_null_order: Literal["nulls_first", "nulls_last"] = "nulls_last",
        access_mode: Literal["automatic", "read_only", "read_write"] = "automatic",
    ) -> None:
        """Initialize DuckDB configuration."""
        self.db_type = db_type
        self.db_path = (
            Path(db_path).expanduser().resolve()
            if db_type == "persistent" and db_path
            else None
        )

        # --- Auto detection ---
        total_ram = psutil.virtual_memory().total
        default_mem = f"{int(total_ram * 0.25 / (1024**3))}GB"
        self.memory_limit = memory_limit or default_mem
        self.threads = threads or os.cpu_count() or 1

        # --- Misc flags ---
        self.enable_progress_bar = enable_progress_bar
        self.read_only = read_only
        self.default_null_order = default_null_order
        self.access_mode = access_mode

    @property
    def connection_uri(self) -> str:
        if self.db_type == "memory":
            return ":memory:"
        if not self.db_path:
            raise ValueError("db_path must be set when db_type='persistent'")
        return str(self.db_path)

    def to_dict(self) -> dict:
        return {
            "db_type": self.db_type,
            "db_path": str(self.db_path) if self.db_path else None,
            "memory_limit": self.memory_limit,
            "threads": self.threads,
            "enable_progress_bar": self.enable_progress_bar,
            "read_only": self.read_only,
            "default_null_order": self.default_null_order,
            "access_mode": self.access_mode,
        }

