"""
Set-up for the checks. You don't need to edit this file.

- Correct answers are saved in practice/answers/.
- Steps you haven't written yet show as SKIPPED instead of FAILED.
"""
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
MAYOR = HERE.parent / "data" / "Poll_By_Poll_Mayor.xlsx"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and call.excinfo is not None \
            and call.excinfo.errisinstance(NotImplementedError):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.location[1] or 0,
                           f"not written yet: {call.excinfo.value}")


@pytest.fixture(scope="session")
def answer_long():
    """Correct result of step 1."""
    return pd.read_csv(HERE / "answers" / "mayor_long.csv.gz")


@pytest.fixture(scope="session")
def answer_summary():
    """Correct result of step 2."""
    return pd.read_csv(HERE / "answers" / "mayor_summary.csv.gz")


@pytest.fixture(scope="session")
def fake_shapes(answer_summary):
    """Fake square subdivisions (so the checks run offline), coded like the
    real layer: AREA_LONG_CODE = "01005"."""
    import geopandas as gpd
    from shapely.geometry import box
    pairs = answer_summary[["ward", "subdiv"]].drop_duplicates()
    pairs = pairs[pairs.subdiv < 90]                 # advance polls have no area
    rows = []
    for w, s in pairs.itertuples(index=False):
        x0 = -79.60 + ((w - 1) % 5) * 0.06 + (s % 8) * 0.0075
        y0 = 43.60 + ((w - 1) // 5) * 0.04 + ((s // 8) % 8) * 0.005
        rows.append({"AREA_LONG_CODE": f"{w:02d}{s:03d}",
                     "geometry": box(x0, y0, x0 + 0.0075, y0 + 0.005)})
    return gpd.GeoDataFrame(rows, crs=4326)


@pytest.fixture(scope="session")
def joined(fake_shapes, answer_summary):
    """Fake shapes with votes attached (input for step 4)."""
    import geopandas as gpd
    codes = answer_summary.assign(AREA_LONG_CODE=[
        f"{w:02d}{s:03d}" for w, s in zip(answer_summary.ward, answer_summary.subdiv)])
    return gpd.GeoDataFrame(fake_shapes.merge(codes, on="AREA_LONG_CODE", how="left"),
                            geometry="geometry", crs=4326)


@pytest.fixture
def same_rows():
    """Compare your table with the answer, ignoring row and column order."""
    def check(mine, correct, columns, sort_by):
        missing = [c for c in columns if c not in mine.columns]
        assert not missing, f"your table is missing columns: {missing}"
        assert len(mine) == len(correct), \
            f"your table has {len(mine):,} rows, the answer has {len(correct):,}"
        a = mine[columns].sort_values(sort_by).reset_index(drop=True)
        b = correct[columns].sort_values(sort_by).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_dtype=False)
    return check
