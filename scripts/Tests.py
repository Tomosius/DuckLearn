# scripts/Tests.py
import subprocess
from pathlib import Path


class Tests:
    """Run and manage test suites with coverage and reports."""

    @staticmethod
    def run():
        """Run basic tests with coverage and incremental testmon cache."""
        print("🧪 Running tests with coverage and testmon cache...\n")
        subprocess.run([
            "uv", "run", "pytest",
            "-q",
            "--testmon",
            "--cov=src",
            "--cov-report=term-missing",
            "--test-report=full",
        ], check=True)
        print("\n✅ Test run complete.")

    @staticmethod
    def full():
        """Run full test suite with coverage (no testmon)."""
        print("🧪 Running full test suite...\n")
        subprocess.run([
            "uv", "run", "pytest",
            "-q",
            "--cov=src",
            "--cov-report=term-missing",
            "--test-report=full",
        ], check=True)
        print("\n✅ Full test suite complete.")

    @staticmethod
    def html():
        """Run tests, generate HTML coverage + HTML test report."""
        print("🧪 Running tests with HTML reports...\n")

        Path("reports").mkdir(exist_ok=True)

        subprocess.run([
            "uv", "run", "pytest",
            "-q",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:reports/coverage",
            "--test-report=full",
            "--html=reports/tests.html",
            "--self-contained-html",
            "--open-html",
            "--repo-url-base=https://github.com/Tomosius/ducklearn/blob/main",
        ], check=True)

        print("\n📊 Reports generated:")
        print("   - 🧪 tests → reports/tests.html")
        print("   - 📈 coverage → reports/coverage/index.html")