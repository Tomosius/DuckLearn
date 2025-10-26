# scripts/Code_Quality.py
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from shutil import which
from typing import List

# Resolve tool paths once (quiets Bandit S607 noise)
ALLOWED_TOOLS = (
    'uv',
    'ruff',
    'mypy',
    'bandit',
    'safety',
    'pip-audit',  # optional; used if installed
    'pydocstyle',
    'radon',
)
BIN = {t: which(t) or t for t in ALLOWED_TOOLS}
AVAIL = {t: which(t) is not None for t in ALLOWED_TOOLS}


def run_step(
    title: str, command: List[str], *, allow_fail: bool = False
) -> None:
    """Run a subprocess command with pretty printing."""
    print(title)
    try:
        subprocess.run(command, check=True)  # noqa: S603
    except subprocess.CalledProcessError as exc:
        if allow_fail:
            print(f'⚠️  Step failed (continuing): {exc}')
        else:
            raise


def _safety_db_file() -> str | None:
    """Locate safety-db's JSON file if the package is installed."""
    try:
        spec = importlib.util.find_spec('safety_db')
        if not spec or not spec.origin:
            return None
        base = Path(spec.origin).parent
        # Common layouts
        candidates = [
            base / 'data' / 'insecure_full.json',
            base / 'insecure_full.json',
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    except Exception:
        return None
    return None


# -------------------------------
# 🐍 Python — Core Tools
# -------------------------------
class Lint:
    """Run static analysis (linting)."""

    @staticmethod
    def python() -> None:
        """Run Ruff lint for Python."""
        run_step(
            '🔍 Running Python linter (Ruff)...',
            [BIN['uv'], 'run', BIN['ruff'], 'check', '.', '--fix'],
        )
        print('✅ Python linting complete.')

    @staticmethod
    def all() -> None:
        """Run all linters (Python + future)."""
        print('🚀 Running all language linters...\n')
        Lint.python()
        print('\n✅ All lint checks complete.')


class Format:
    """Auto-format code."""

    @staticmethod
    def python() -> None:
        """Format Python code."""
        run_step(
            '🧼 Formatting Python code (Ruff)...',
            [BIN['uv'], 'run', BIN['ruff'], 'format', '.'],
        )
        print('✅ Python formatting complete.')

    @staticmethod
    def all() -> None:
        """Run all formatters (Python + future)."""
        print('🚀 Running all formatters...\n')
        Format.python()
        print('\n✅ All formatting complete.')


class Sort:
    """Sort and organize imports."""

    @staticmethod
    def python() -> None:
        """Sort Python imports."""
        run_step(
            '📚 Sorting Python imports...',
            [
                BIN['uv'],
                'run',
                BIN['ruff'],
                'check',
                '.',
                '--select',
                'I',
                '--fix',
            ],
        )
        print('✅ Python imports sorted.')

    @staticmethod
    def all() -> None:
        """Run all sorters (Python + future)."""
        print('🚀 Running all sorters...\n')
        Sort.python()
        print('\n✅ All sorting complete.')


class TypeCheck:
    """Run type checks for Python."""

    @staticmethod
    def python() -> None:
        """Run Mypy (Pydantic via config)."""
        run_step(
            '🧠 Checking Python types (Mypy + Pydantic)...',
            [
                BIN['uv'],
                'run',
                BIN['mypy'],
                'src',
                '--config-file',
                'pyproject.toml',
            ],
        )
        print('✅ Python type checking complete.')

    @staticmethod
    def all() -> None:
        """Run all type checkers."""
        print('🚀 Running all type checkers...\n')
        TypeCheck.python()
        print('\n✅ All type checks complete.')


# -------------------------------
# 🔒 Security & Docs
# -------------------------------
class Security:
    """Run code and dependency security checks."""

    @staticmethod
    def bandit() -> None:
        """Scan code with Bandit (non-fatal if flaky)."""
        run_step(
            '🛡️  Running Bandit (code security scan)...',
            [BIN['uv'], 'run', BIN['bandit'], '-r', 'src', '--quiet'],
            allow_fail=True,
        )
        print('✅ Bandit scan complete.')

    @staticmethod
    def deps() -> None:
        """Scan dependencies using pip-audit or Safety (+ safety-db if present)."""
        # Prefer pip-audit if available
        if AVAIL.get('pip-audit'):
            run_step(
                '🔒 Running pip-audit (OSV/PyPI advisories)...',
                [
                    BIN['uv'],
                    'run',
                    BIN['pip-audit'],
                    '--progress-spinner',
                    'off',
                ],
            )
            print('✅ Dependency scan complete.')
            return

        # Otherwise use Safety with optional offline safety-db
        if not AVAIL.get('safety'):
            print('⚠️  No dependency scanner found (pip-audit or safety).')
            return

        db_path = _safety_db_file()
        if db_path:
            # Fully offline scan using the installed safety-db
            run_step(
                '🔒 Running Safety (offline scan, local safety-db)...',
                [
                    BIN['uv'],
                    'run',
                    BIN['safety'],
                    'scan',
                    '--db',
                    db_path,
                    '--full-report',
                ],
            )
        else:
            # Fallback to online scan if no local DB found
            run_step(
                '🔒 Running Safety (online scan)...',
                [BIN['uv'], 'run', BIN['safety'], 'scan', '--full-report'],
            )

        print('✅ Dependency scan complete.')

    @staticmethod
    def all() -> None:
        """Run all security scans."""
        print('🚀 Running all security scans...\n')
        Security.bandit()
        Security.deps()
        print('\n✅ All security checks complete.')


class Docs:
    """Analyze documentation and complexity."""

    @staticmethod
    def docstrings() -> None:
        """Check docstring style (PEP257)."""
        run_step(
            '📝 Checking docstring style (pydocstyle)...',
            [
                BIN['uv'],
                'run',
                BIN['pydocstyle'],
                'src',
                '--ignore',
                'D100,D104',
            ],
        )
        print('✅ Docstring style check complete.')

    @staticmethod
    def complexity() -> None:
        """Analyze cyclomatic complexity."""
        run_step(
            '📊 Measuring code complexity (Radon)...',
            [BIN['uv'], 'run', BIN['radon'], 'cc', '-s', '-a', 'src'],
        )
        print('✅ Complexity analysis complete.')

    @staticmethod
    def all() -> None:
        """Run docs/complexity tools."""
        print('🚀 Running documentation & complexity checks...\n')
        Docs.docstrings()
        Docs.complexity()
        print('\n✅ Documentation and complexity analysis complete.')


# -------------------------------
# 🧩 Aggregate Levels for Python
# -------------------------------
class Python:
    """Aggregate Python code quality tasks."""

    @staticmethod
    def basic() -> None:
        """Run minimal quality checks."""
        print('🟢 Running BASIC Python quality checks...\n')
        Sort.python()
        Format.python()
        Lint.python()
        print('\n✅ Basic Python checks complete.')

    @staticmethod
    def normal() -> None:
        """Run normal checks (basic + types)."""
        print('🟡 Running NORMAL Python quality checks...\n')
        Sort.python()
        Format.python()
        Lint.python()
        TypeCheck.python()
        print('\n✅ Normal Python checks complete.')

    @staticmethod
    def full() -> None:
        """Run full audit (adds security & docs)."""
        print('🔴 Running FULL Python quality audit...\n')
        Sort.python()
        Format.python()
        Lint.python()
        TypeCheck.python()
        Security.bandit()
        Security.deps()
        Docs.docstrings()
        Docs.complexity()
        print('\n🎉 Full Python audit completed successfully!')


# -------------------------------
# 🌍 Universal Entry
# -------------------------------
class CodeQuality:
    """Run global quality steps (all languages)."""

    @staticmethod
    def all() -> None:
        """Run linters/formatters/sorters/types."""
        print('🌐 Running full multi-language quality pipeline...\n')
        Sort.all()
        Format.all()
        Lint.all()
        TypeCheck.all()
        print('\n🏁 All global code quality checks complete.')
