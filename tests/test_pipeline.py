"""
Run with:  python -m pytest -q

Each test states one thing that must stay true. If you change the parser
later and a test fails, it tells you exactly which promise you broke.
"""
import os
from pathlib import Path

import pytest

from election_map import read_poll_by_poll, summarize
from election_map.geo import detect_key, join
from tests.fake_boundaries import fake_boundaries

DATA = Path(os.environ.get("ELECTION_DATA", "data"))
MAYOR = DATA / "Poll_By_Poll_Mayor.xlsx"
needs_data = pytest.mark.skipif(not MAYOR.exists(), reason=f"put the .xlsx files in {DATA}/")


@needs_data
def test_mayor_total_matches_official():
    long = read_poll_by_poll(MAYOR)
    assert long["votes"].sum() == 982_660          # from the sheets' own totals rows
    assert long["ward"].nunique() == 25


@needs_data
def test_every_file_parses():
    # parse_sheet() raises ParseError if any block disagrees with its Totals row
    for f in DATA.glob("Poll_By_Poll_*.xlsx"):
        assert len(read_poll_by_poll(f)) > 0, f


@needs_data
def test_ties_are_not_given_to_anyone():
    s = summarize(read_poll_by_poll(MAYOR))
    tied = s[s["winner"] == "Tie"]
    assert (tied["margin_pct"] == 0).all()


@needs_data
def test_one_ward_does_not_fool_key_detection():
    # Regression test: with only ward 10, OBJECTID numbers like 1001 used to
    # "match" by coincidence. Detecting on all wards (detect_with) prevents it.
    long = read_poll_by_poll(MAYOR)
    full = summarize(long)
    shapes = fake_boundaries(full)
    one_ward = summarize(long[long.ward == 10])
    _, report = join(shapes, one_ward, detect_with=full)
    assert report["boundary_field"] == "AREA_LONG_CODE"


@needs_data
@pytest.mark.parametrize("fmt_name,fmt", [
    ("WWSSS (01005)", lambda w, s: f"{w:02d}{s:03d}"),
    ("W-S (1-5)", lambda w, s: f"{w}-{s}"),
])
def test_key_detection_finds_the_right_field(fmt_name, fmt):
    s = summarize(read_poll_by_poll(MAYOR))
    shapes = fake_boundaries(s, key="SUBDIV_CODE", fmt=fmt)
    field, found, rate = detect_key(shapes, s)
    assert (field, found) == ("SUBDIV_CODE", fmt_name)
    assert rate == 1.0
    gdf, report = join(shapes, s)
    assert report["shapes_without_results"] == 0
    assert report["results_without_shapes"] > 0     # the 90+ advance polls
