# Contributing

Contributions are welcome.

## Development Setup

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
pip install -e ".[dev]"
```

## Checks

Run before opening a pull request:

```bash
ruff format src tests examples
ruff check src tests examples
mypy src
pytest
python3 -m build
```

## Good First Contributions

Good first areas include:

- documentation
- examples
- tests
- schedulers
- spaces
- export formats
- visualization helpers
- analysis tools

## Pull Request Expectations

A pull request should include:

- a clear description
- tests when changing code
- documentation when adding public features
- passing CI checks
