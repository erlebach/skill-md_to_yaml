# Using the "uv" package

## Install uv

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/). 
curl is preferred. 

## Synchronize `pyproject.toml`

```bash
uv sync
```

## Activate the Python environment

```bash
source .venv/bin/activate
```

## Use Python 

- Python is now available for use via `python file.py ...`
- Alternatively, `uv run python ...`

## Deactivate the environment

```bash
deactivate
```
