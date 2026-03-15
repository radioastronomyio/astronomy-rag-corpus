"""
Tests for BBL parser.
"""

from pathlib import Path

import pytest

from src.extraction.bbl_parser import parse_bbl
from src.logging_config import setup_logging

setup_logging()


def test_parse_bbl_seed_paper():
    """Test parsing the seed paper's .bbl file."""
    bbl_path = Path("test_output/extracted/2411.00148/desi_bgs_voids_y1.bbl")

    if not bbl_path.exists():
        pytest.skip(f"BBL file not found: {bbl_path}")

    references = parse_bbl(bbl_path)

    # Verify references dict is non-empty
    assert len(references) > 0, "References dict should be non-empty"

    # Find a reference with all fields populated
    complete_refs = [
        ref for ref in references.values() if ref.authors and ref.title and ref.year
    ]
    assert len(complete_refs) > 0, (
        "At least one reference should have all fields populated"
    )

    # Verify raw field is non-empty for every reference
    for cite_key, ref in references.items():
        assert cite_key, f"Cite key should not be empty"
        assert ref.raw, f"Reference {cite_key} should have non-empty raw field"
