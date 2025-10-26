# ================================================================
# 🦆 DuckLearn Makefile
# ------------------------------------------------
# Author: Tomas Pecukevicius
# License: Apache-2.0
# ------------------------------------------------
# This Makefile centralizes key developer tasks for the DuckLearn project.
# Run any command with:
#     make <target>
#
# Example:
#     make setup      # Install Git hooks
#     make licenses   # Update license summaries
# ================================================================

# ================================================================
# 🧭 General Settings
# ================================================================

# Default shell to use for all commands
SHELL := /bin/bash

# Fail if any command fails (for reliability)
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ================================================================
# 📘 Help: list available targets
# ================================================================
.PHONY: help
help:
	@echo ""
	@echo "🦆 DuckLearn Project Tasks"
	@echo "================================================"
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Core setup:"
	@echo "  make setup       → Install pre-commit Git hooks"
	@echo ""
	@echo "Maintenance:"
	@echo "  make licenses    → Regenerate THIRD_PARTY_LICENSES.md"
	@echo "  make bump        → Bump project version & update changelog"
	@echo "  make hooks       → Run all pre-commit hooks on the repo"
	@echo "  make clean       → Remove caches, build artifacts, and temp files"
	@echo ""
	@echo "Info:"
	@echo "  make help        → Show this help message"
	@echo ""

# ================================================================
# ⚙️ Setup: install Git hooks for commit validation
# ================================================================
.PHONY: setup
setup:
	@echo "🔧 Installing pre-commit Git hooks..."
	uv run pre-commit install --hook-type commit-msg
	@echo "✅ Hooks installed successfully."

# ================================================================
# 🧾 Licensing: auto-generate dependency license summary
# ================================================================
.PHONY: licenses
licenses:
	@echo "🧾 Generating THIRD_PARTY_LICENSES.md..."
	uv run pip-licenses --format=markdown --with-urls --output-file THIRD_PARTY_LICENSES.md
	@echo "✅ THIRD_PARTY_LICENSES.md updated successfully."

# ================================================================
# 🚀 Versioning: bump project version & changelog
# ================================================================
.PHONY: bump
bump:
	@echo "🚀 Bumping version using Commitizen..."
	uv run cz bump
	@echo "✅ Version bumped and changelog updated."
	@echo ""
	@echo "💡 Reminder: Don't forget to push tags!"
	@echo "   git push && git push --tags"

# ================================================================
# 🧹 Code Quality: run all pre-commit hooks
# ================================================================
.PHONY: hooks
hooks:
	@echo "🧹 Running all pre-commit hooks..."
	uv run pre-commit run --all-files
	@echo "✅ All hooks completed."

# ================================================================
# 🧼 Cleanup: remove build artifacts and caches
# ================================================================
.PHONY: clean
clean:
	@echo "🧼 Cleaning up build and cache artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info || true
	@echo "✅ Cleanup complete."