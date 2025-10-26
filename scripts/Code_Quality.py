import subprocess


class Lint:
    """Run static analysis (linting) for Python files using Ruff."""

    @staticmethod
    def python():
        """Run Ruff lint checks with auto-fix for trivial issues."""
        print('🔍 Running Ruff linter (Python)...')
        subprocess.run(
            ['uv', 'run', 'ruff', 'check', '.', '--fix'], check=True
        )
        print('✅ Linting complete — no critical issues found.')


class Format:
    """Auto-format Python code using Ruff."""

    @staticmethod
    def python():
        """Apply code formatting fixes."""
        print('🧼 Formatting Python code with Ruff...')
        subprocess.run(['uv', 'run', 'ruff', 'format', '.'], check=True)
        print('✅ Formatting complete.')


class Sort:
    """Sort Python imports using Ruff."""

    @staticmethod
    def python():
        """Sort and fix import order."""
        print('📚 Sorting imports with Ruff...')
        subprocess.run(
            ['uv', 'run', 'ruff', 'check', '.', '--select', 'I', '--fix'],
            check=True,
        )
        print('✅ Import sorting complete.')


class TypeCheck:
    """Run static type checking using Mypy (with Pydantic awareness)."""

    @staticmethod
    def python():
        """Check type correctness and model definitions."""
        print('🧠 Running Mypy static type checks (with Pydantic plugin)...')
        subprocess.run(
            [
                'uv',
                'run',
                'mypy',
                'src',
                '--config-file',
                'pyproject.toml',
            ],
            check=True,
        )
        print('✅ Type checking complete — no issues found.')


class Python:
    """Aggregate all Python code quality tasks."""

    @staticmethod
    def all():
        """Run sorting, formatting, linting, and type checking in sequence."""
        print('🧩 Running full Python code quality pipeline...\n')
        Sort.python()
        Format.python()
        Lint.python()
        TypeCheck.python()
        print('\n🎉 All Python code quality checks completed successfully!')
