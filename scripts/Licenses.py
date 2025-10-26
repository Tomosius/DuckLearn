import subprocess


class Licenses:
    """Generate and refresh license reports."""

    @staticmethod
    def generate():
        """Generate or refresh THIRD_PARTY_LICENSES.md."""
        print('🧾 Generating THIRD_PARTY_LICENSES.md...')
        subprocess.run(
            [
                'uv',
                'run',
                'pip-licenses',
                '--format=markdown',
                '--with-urls',
                '--output-file',
                'THIRD_PARTY_LICENSES.md',
            ],
            check=True,
        )
        print('✅ THIRD_PARTY_LICENSES.md updated successfully.')
