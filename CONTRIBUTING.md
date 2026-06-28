# Contributing

## Development setup

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Quality checks

Run these before opening a pull request:

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest
python -m build
```

## Contribution rules

- Add or update tests for behavior changes.
- Keep the public API small.
- Document any public API addition.
- Avoid adding heavy dependencies to the core package.
- Put experimental features under an explicit experimental namespace in future releases.

## Issue templates

Before opening a pull request, consider whether an issue should be created first.
ABMForge provides issue templates for bug reports, feature requests, and
reproducibility reports.

Use the reproducibility report template for problems involving scenarios,
experiment archives, manifests, artifact checksums, deterministic seeds,
ODD outputs, or archive validation.

Good issues should include the ABMForge version or commit, Python version,
operating system, installation method, exact commands, and a minimal
reproducible example when possible.
