# scripts/Setup.py
import subprocess

from .Licenses import Licenses


class Setup:
    """Environment setup and dependency management for DuckLearn."""

    # ------------------------------------------------------------
    # 📦 INSTALLATION
    # ------------------------------------------------------------

    @staticmethod
    def install():
        """Install only base dependencies (runtime/production setup)."""
        print('📦 Installing base dependencies...')
        subprocess.run(['uv', 'sync'], check=True)
        print('✅ Base dependencies installed successfully.')

    @staticmethod
    def install_all():
        """Install all dependencies + dev tools + Git hooks."""
        print('🧰 Setting up full DuckLearn development environment...')

        # 1️⃣ Install everything (all dependency groups)
        subprocess.run(['uv', 'sync', '--all-groups'], check=True)

        # 2️⃣ Install pre-commit hooks
        print('🧩 Installing Git hooks...')
        subprocess.run(
            [
                'uv',
                'run',
                'pre-commit',
                'install',
                '--hook-type',
                'commit-msg',
            ],
            check=True,
        )

        # 3️⃣ Generate THIRD_PARTY_LICENSES.md
        # 3️⃣ Generate THIRD_PARTY_LICENSES.md via shared class
        Licenses.generate()  # ✅ reuse existing code

        print('✅ Full developer setup complete! 🦆')

    # ------------------------------------------------------------
    # 🔄 UPGRADES
    # ------------------------------------------------------------

    @staticmethod
    def update():
        """Upgrade all dependencies across all groups."""
        print('🔄 Updating ALL dependencies (base + groups)...')
        subprocess.run(['uv', 'lock', '--upgrade'], check=True)
        subprocess.run(['uv', 'sync', '--all-groups'], check=True)
        print('✅ All dependencies updated and synced.')
