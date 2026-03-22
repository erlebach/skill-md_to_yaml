"""
Wave 0 test stubs for Phase 2 compiler tests (COMP-01 through COMP-06, ADA-02 through ADA-05).
All functions are xfail stubs — implementation in Plan 03.
"""
import pytest


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_compile_produces_html():
    """COMP-01: Compiler produces valid HTML output from a deck YAML."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_all_layout_types_render():
    """COMP-02: All 12 layout types render without error."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_deterministic_output():
    """COMP-03: Compiler output is deterministic (same input → same output)."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_cli_invocation():
    """COMP-04: CLI can be invoked and produces output file."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_css_vars_embedded():
    """COMP-05: CSS custom properties (theme vars) are embedded in output HTML."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_keyboard_js_embedded():
    """COMP-06 / ADA-05: Keyboard navigation JavaScript is embedded in output HTML."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_aria_carousel_markup():
    """ADA-02: Slide container has role=region or appropriate ARIA carousel markup."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_skip_link_present():
    """ADA-03: Skip-to-content link is present in output HTML."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_aria_labelledby():
    """ADA-04: Slides have aria-labelledby linking to their heading."""
    assert False


@pytest.mark.xfail(reason="stub — implementation in Plan 03")
def test_cli_error_exit_code():
    """Error path: CLI exits with non-zero code on invalid input."""
    assert False
