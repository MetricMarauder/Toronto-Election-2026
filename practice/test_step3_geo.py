"""
Checkers for STEP 3 (practice/my_election_map/geo.py).

These use FAKE square boundaries (tests/fake_boundaries.py) coded like the
real layer, so they run offline in seconds. Your real run checks the real ones.

Run:  python -m pytest practice -rs -k 3a      (or 3b, 3c)
"""
import geopandas as gpd
import pytest

from election_map import geo as answer
from my_election_map import geo as mine


# ---------------------------------------------------------------- 3a
@pytest.mark.parametrize("ward,subdiv,expected", [
    (1, 5, "01005"),
    (10, 1, "10001"),
    (25, 112, "25112"),
    (3, 99, "03099"),
])
def test_3a_make_key(ward, subdiv, expected):
    assert mine.make_key(ward, subdiv) == expected


# ---------------------------------------------------------------- 3b
def test_3b_load_and_reproject(fake_shapes, tmp_path):
    # Save the shapes in "web Mercator" (EPSG:3857, what your QGIS project uses)...
    path = tmp_path / "subdivisions.gpkg"
    fake_shapes.to_crs(3857).to_file(path)
    # ...and your loader must hand them back in latitude/longitude.
    shapes = mine.load_boundaries(path)
    assert isinstance(shapes, gpd.GeoDataFrame)
    assert len(shapes) == len(fake_shapes)
    assert shapes.crs.to_epsg() == 4326
    west, south, east, north = shapes.total_bounds
    assert -80 < west < east < -79 and 43 < south < north < 44, "should be around Toronto"
    mine.load_boundaries(str(path))                  # a plain text path works too


def test_3b_missing_file():
    with pytest.raises(FileNotFoundError):
        mine.load_boundaries("data/no_such_file.gpkg")


# ---------------------------------------------------------------- 3c
def answer_join(shapes, summary):
    return answer.join(shapes, summary, field="AREA_LONG_CODE", key_format="WWSSS (01005)")


def test_3c_join_report(fake_shapes, answer_summary):
    gdf, report = mine.join(fake_shapes, answer_summary)
    _, expected = answer_join(fake_shapes, answer_summary)
    for k in ["matched", "shapes_without_results", "results_without_shapes"]:
        assert report[k] == expected[k], f"report[{k!r}] is {report[k]}, expected {expected[k]}"
    assert report["shapes_without_results"] == 0
    assert report["results_without_shapes"] > 0, "advance/mail polls (90+) have no shape"


def test_3c_join_table(fake_shapes, answer_summary):
    gdf, _ = mine.join(fake_shapes, answer_summary)
    assert isinstance(gdf, gpd.GeoDataFrame), "keep it a GeoDataFrame so it can be mapped"
    assert len(gdf) == len(fake_shapes), "one row per SHAPE"
    for col in ["winner", "total", "winner_pct"]:
        assert col in gdf.columns
    row = gdf[gdf["AREA_LONG_CODE"] == "01001"].iloc[0]
    assert row["total"] == 466                       # ward 1, subdivision 1


def test_3c_one_ward_only(fake_shapes, answer_summary):
    # Results for ward 10 only: every OTHER shape should count as "without results".
    one_ward = answer_summary[answer_summary["ward"] == 10]
    gdf, report = mine.join(fake_shapes, one_ward)
    _, expected = answer_join(fake_shapes, one_ward)
    assert report["matched"] == expected["matched"]
    assert report["shapes_without_results"] == expected["shapes_without_results"]
    assert len(gdf) == len(fake_shapes)
