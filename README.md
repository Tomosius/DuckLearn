# 🦆 DuckLearn
### An Open Learning Framework Powered by DuckDB

---

## 📘 Overview

**DuckLearn** is an experimental open learning framework built on top of [DuckDB](https://duckdb.org).
It aims to make data exploration, analysis, and lightweight machine learning accessible directly within the DuckDB ecosystem — with a focus on educational use, transparency, and modular design.

> Status: **Alpha** — expect rapid iteration.

---

## 🚀 Features

- 🪶 **DuckDB-native**: built on DuckDB’s analytical engine
- 🧩 **Modular design**: extendable with Pro and Private editions
- 🧠 **Learning-oriented**: simple, clear APIs and examples
- 🧾 **Modern setup**: powered by [`uv`](https://docs.astral.sh/uv) (fast dependency + env manager)
- 🧰 **Dev workflow**: Commitizen, pre-commit hooks, and automated third‑party license report

---

## 🧭 Quick Start (Powered by uv)

DuckLearn uses [**uv**](https://docs.astral.sh/uv/) as its dependency and environment manager.
It replaces `pip` and `venv` with faster resolution and reproducible environments.

### 1) Install uv

If you don’t have it yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2) Clone the repository

```bash
git clone https://github.com/Tomosius/DuckLearn.git
cd DuckLearn
```

### 3) One-command setup

```bash
make setup
```

This will automatically:

- install all project dependencies and developer tools (via `uv sync`)
- install Git hooks for commit message validation (pre-commit / Commitizen)
- generate / refresh `THIRD_PARTY_LICENSES.md`

That’s it — you’re ready to code 🎉

---

## 🧩 Development Workflow

Common tasks (via `Makefile`):

| Command        | Description                                         |
|----------------|-----------------------------------------------------|
| `make setup`   | Install deps, Git hooks, and generate license list  |
| `make licenses`| Refresh `THIRD_PARTY_LICENSES.md`                   |
| `make hooks`   | Run all pre-commit hooks on the codebase            |
| `make bump`    | Bump version + changelog using Commitizen           |
| `make clean`   | Remove caches and build artifacts                   |
| `make help`    | Show all available tasks                            |

Conventional Commits are encouraged. Use:

```bash
cz commit
# or
cz c
```

To bump versions and update the changelog based on commit history:

```bash
make bump
# (equivalent to: uv run cz bump)
```

---

## 🧾 License & Notices

- Project license: **Apache License 2.0** — see [LICENSE](./LICENSE)
- Acknowledgements & attribution: see [NOTICE](./NOTICE)
- Full dependency license report: see [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md)

If you distribute binaries, wheels, or containers, please include the three files above.

---

## 🧠 Project Structure

```
DuckLearn/
├── LICENSE
├── NOTICE
├── THIRD_PARTY_LICENSES.md
├── pyproject.toml
├── README.md
├── src/
│   └── ducklearn/
└── tests/
```

---

## 💬 Contributing

Contributions are welcome!

1. Run `make setup`
2. Use `cz commit` for Conventional Commits
3. Run `make hooks` before opening a PR

Feel free to open issues or discussions in the repository.

---

## 👤 Author

**Tomas Pecukevicius**  
📧 contact@pecuk.dev  
🔗 https://github.com/Tomosius
