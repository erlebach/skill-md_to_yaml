"""
Wave 0 test stubs for Phase 2 validator tests (ADA-01, ADA-06, ADA-07, ADA-08).
All functions are xfail stubs — implementation in Plan 03.
"""
import pytest


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_missing_alt_text_error():
    """ADA-01: Validator raises error when image slide is missing alt text."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_valid_alt_text_no_error():
    """ADA-01: Validator passes when all image slides have alt text."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_invalid_contrast_error():
    """ADA-06: Validator raises error when contrast ratio is below 4.5:1."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_valid_contrast_no_error():
    """ADA-06: Validator passes when contrast ratio meets 4.5:1 threshold."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_no_accent_color_no_error():
    """ADA-06: Validator passes when no accent color is specified (no contrast to check)."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_layout_variety_warning():
    """ADA-07: Validator emits warning when all slides use the same layout type."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_no_layout_variety_warning_for_two():
    """ADA-07: Validator does not warn when deck has only two slides."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_bullet_limit_warning():
    """ADA-08: Validator emits warning when a slide exceeds bullet point limit."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_bullet_limit_ok_for_five():
    """ADA-08: Validator passes when slide has exactly five bullet points."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_contrast_dark_theme_amber_passes():
    """ADA-06: Dark theme with amber accent passes contrast check."""
    assert False
