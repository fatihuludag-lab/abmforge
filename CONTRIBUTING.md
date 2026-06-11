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
