import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / 'fixtures'


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def valid_deck_path():
    return FIXTURES_DIR / 'valid_deck.yaml'


@pytest.fixture
def invalid_missing_alt_path():
    return FIXTURES_DIR / 'invalid_missing_alt.yaml'


@pytest.fixture
def invalid_unknown_field_path():
    return FIXTURES_DIR / 'invalid_unknown_field.yaml'


@pytest.fixture
def minimal_metadata_path():
    return FIXTURES_DIR / 'deck_metadata_minimal.yaml'


@pytest.fixture
def two_column_path():
    return FIXTURES_DIR / 'two_column_variants.yaml'
