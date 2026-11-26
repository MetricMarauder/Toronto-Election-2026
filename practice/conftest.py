"""
Shared set-up for the practice checkers. You don't need to edit this file.

Two things happen here:
1. Fixtures: data every checker needs. The correct answers are saved as
   tables in practice/answers/, and pytest hands them to any test function
   that names them as an argument.
2. A friendly rule: if your function still says `raise NotImplementedError`,
   its checks show as SKIPPED ("not written yet") instead of FAILED.
   So a run of all the checkers doubles as a progress bar.
"""
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ANSWERS = Path(__file__).resolve().parent / "answers"
MAYOR = DATA / "Poll_By_Poll_Mayor.xlsx"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and call.excinfo is not None \
            and call.excinfo.errisinstance(NotImplementedError):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.location[1] or 0,
                           f"not written yet: {call.excinfo.value}")


def answer(name):
    """Load a saved correct answer, e.g. answer("mayor_long")."""
    return pd.read_csv(ANSWERS / f"{name}.csv.gz")


# ---------------------------------------------------------------- fixtures
@pytest.fixture(scope="session")
def mayor_sheets():
    """Every sheet of the Mayor workbook, raw (header=None): {name: DataFrame}."""
    if not MAYOR.exists():
        pytest.skip(f"put the Poll_By_Poll_*.xlsx files in {DATA}/")
    return pd.read_excel(MAYOR, sheet_name=None, header=None)


@pytest.fixture(scope="session")
def answer_long():
    """The correct long table for the Mayor file (Step 1's answer)."""
    return answer("mayor_long")


@pytest.fixture(scope="session")
def answer_summary():
    """The correct per-subdivision summary, with compare=Chow vs Bradford (Step 2's answer)."""
    return answer("mayor_summary")


@pytest.fixture(scope="session")
def fake_shapes(answer_summary):
    """FAKE square 'subdivisions', a grid over Toronto, one per subdivision,
    coded like the real layer: AREA_LONG_CODE = "01005".

    Fake shapes let the checkers run offline in seconds. Your real run
    checks the real boundaries.
    """
    import geopandas as gpd
    from shapely.geometry import box
    pairs = answer_summary[["ward", "subdiv"]].drop_duplicates()
    pairs = pairs[pairs.subdiv < 90]                 # advance polls have no area
    rows = []
    for i, (w, s) in enumerate(pairs.itertuples(index=False)):
        col, row = (w - 1) % 5, (w - 1) // 5         # 5x5 grid of wards
        x0 = -79.60 + col * 0.06 + (s % 8) * 0.0075
        y0 = 43.60 + row * 0.04 + ((s // 8) % 8) * 0.005
        rows.append({"OBJECTID": i + 1, "AREA_LONG_CODE": f"{w:02d}{s:03d}",
                     "geometry": box(x0, y0, x0 + 0.0075, y0 + 0.005)})
    return gpd.GeoDataFrame(rows, crs=4326)


@pytest.fixture(scope="session")
def joined(fake_shapes, answer_summary):
    """Fake shapes with the votes already attached: ready to map (Step 4's input)."""
    import geopandas as gpd
    codes = answer_summary.assign(
        AREA_LONG_CODE=[f"{w:02d}{s:03d}" for w, s in zip(answer_summary.ward, answer_summary.subdiv)])
    table = fake_shapes.merge(codes, on="AREA_LONG_CODE", how="left")
    return gpd.GeoDataFrame(table, geometry="geometry", crs=fake_shapes.crs)


@pytest.fixture
def same_rows():
    """Compare your table with the answer, ignoring row order and column order."""
    def check(mine, correct, columns, sort_by):
        missing = [c for c in columns if c not in mine.columns]
        assert not missing, f"your table is missing these columns: {missing}"
        assert len(mine) == len(correct), \
            f"your table has {len(mine):,} rows, the answer has {len(correct):,}"
        a = mine[columns].sort_values(sort_by).reset_index(drop=True)
        b = correct[columns].sort_values(sort_by).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_dtype=False)
    return check
