from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from shutil import which

# --------------------------------------------------------
# Resolve executables
# --------------------------------------------------------
TOOLS = (
    'uv',
    'npm',
    'uvicorn',
)
BIN = {t: which(t) or t for t in TOOLS}

# Project root detection (assumes /scripts is next to /src and /frontend)
ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / 'frontend'
BACKEND_DIR = ROOT / 'src'


# --------------------------------------------------------
# Helpers
# --------------------------------------------------------
def run_step(
    title: str, command: list[str], *, cwd: Path | None = None
) -> None:
    """Run a subprocess command with pretty printing."""
    print(f'\n🚀 {title}')
    try:
        subprocess.run(command, check=True, cwd=cwd)  # noqa: S603
        print(f'✅ {title} — done.')
    except subprocess.CalledProcessError as exc:
        print(f'❌ {title} — failed:\n  {exc}')
        sys.exit(exc.returncode)


# --------------------------------------------------------
# 🧩 Run Commands
# --------------------------------------------------------
def run_backend() -> None:
    """Run FastAPI backend using Uvicorn."""
    run_step(
        'Running FastAPI backend (Uvicorn)...',
        [
            BIN['uv'],
            'run',
            BIN['uvicorn'],
            'src.ducklearn.app:app',
            '--reload',
        ],
        cwd=ROOT,
    )


def run_frontend() -> None:
    """Run SvelteKit frontend in dev mode."""
    run_step(
        'Running SvelteKit frontend (npm run dev)...',
        [BIN['npm'], 'run', 'dev'],
        cwd=FRONTEND_DIR,
    )


def run_both() -> None:
    """Run both backend and frontend concurrently."""
    print('\n🌐 Running both backend & frontend...')
    backend_proc = subprocess.Popen(  # noqa: S603
        [
            BIN['uv'],
            'run',
            BIN['uvicorn'],
            'src.ducklearn.app:app',
            '--reload',
        ],
        cwd=ROOT,
    )
    frontend_proc = subprocess.Popen(  # noqa: S603
        [BIN['npm'], 'run', 'dev'],
        cwd=FRONTEND_DIR,
    )
    print('✅ Both backend and frontend are running.\nPress Ctrl+C to stop.')
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print('\n🛑 Stopping servers...')
        backend_proc.terminate()
        frontend_proc.terminate()
        print('✅ Clean shutdown complete.')


# --------------------------------------------------------
# 🏗️ Build Commands
# --------------------------------------------------------
def build_backend() -> None:
    """Build backend Python package."""
    run_step(
        'Building Python backend (wheel via uv)...',
        [BIN['uv'], 'build'],
        cwd=ROOT,
    )


def build_frontend() -> None:
    """Build SvelteKit static frontend."""
    run_step(
        'Building SvelteKit frontend...',
        [BIN['npm'], 'run', 'build'],
        cwd=FRONTEND_DIR,
    )


def build_both() -> None:
    """Build both backend and frontend."""
    print('\n🔧 Building full stack (backend + frontend)...')
    build_backend()
    build_frontend()
    print('\n🎉 Full stack build complete.')


# --------------------------------------------------------
# 📦 Package Command
# --------------------------------------------------------
def package() -> None:
    """Build full distributable package (wheel + static frontend)."""
    print('\n📦 Building full production package...')
    build_backend()
    build_frontend()

    static_target = ROOT / 'src' / 'ducklearn' / 'static'
    dist_frontend = FRONTEND_DIR / 'build'

    if dist_frontend.exists():
        run_step(
            f'Copying frontend build → {static_target}',
            ['rsync', '-a', str(dist_frontend) + '/', str(static_target)],
        )

    print(
        '\n🎁 Final package ready in /dist (wheel) and /src/ducklearn/static (frontend).'
    )


# --------------------------------------------------------
# 🧭 CLI entrypoint
# --------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Run or build DuckLearn stack.'
    )
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('run_backend')
    sub.add_parser('run_frontend')
    sub.add_parser('run_both')
    sub.add_parser('build_backend')
    sub.add_parser('build_frontend')
    sub.add_parser('build_both')
    sub.add_parser('package')

    args = parser.parse_args()

    match args.cmd:
        case 'run_backend':
            run_backend()
        case 'run_frontend':
            run_frontend()
        case 'run_both':
            run_both()
        case 'build_backend':
            build_backend()
        case 'build_frontend':
            build_frontend()
        case 'build_both':
            build_both()
        case 'package':
            package()
        case _:
            parser.print_help()
